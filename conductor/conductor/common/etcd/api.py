#
# -------------------------------------------------------------------------
#   Copyright (C) 2021 Wipro Limited.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# -------------------------------------------------------------------------
#

import copy
import etcd3
from grpc import RpcError
import json
from oslo_config import cfg

from conductor.common.etcd.utils import EtcdClientException
from conductor.common.etcd.utils import validate_schema


CONF = cfg.CONF

ETCD_API_OPTS = [
    cfg.StrOpt('host',
               default='localhost',
               help='host/ip for etcd'),
    cfg.StrOpt('port',
               default='2379',
               help='port for etcd'),
    cfg.StrOpt('username',
               default='root',
               help='Username for authentication'),
    cfg.StrOpt('password',
               default='root',
               help='Password for authentication'),
]

CONF.register_opts(ETCD_API_OPTS, group='etcd_api')


class EtcdAPI(object):

    def __init__(self):
        self.host = CONF.etcd_api.host
        self.port = CONF.etcd_api.port
        self.user = CONF.etcd_api.username
        self.password = CONF.etcd_api.password

    def get_client(self):
        try:
            return etcd3.client(host=self.host, port=self.port,
                                user=self.user, password=self.password,
                                grpc_options={
                                    'grpc.http2.true_binary': 1,
                                    'grpc.http2.max_pings_without_data': 0,
                                    'grpc.max_send_message_length': 50 * 1024 * 1024,
                                    'grpc.max_receive_message_length': 50 * 1024 * 1024,
                                }.items())
        except RpcError as rpc_error:
            raise EtcdClientException("Failed to establish connection with ETCD. GRPC {}".format(rpc_error.code()))

    def get_raw_value(self, key):
        return self.get_client().get(key)[0]

    def get_value(self, key):
        raw_value = self.get_raw_value(key)
        if raw_value:
            return json.loads(raw_value)
        return None

    def get_values_prefix(self, key_prefix, filter_name=None, filter_value=None):
        values = {kv[1].key.decode().lstrip(key_prefix): json.loads(kv[0])
                  for kv in self.get_client().get_prefix(key_prefix)}
        if not filter_name or not filter_value:
            return values

        return dict(filter(lambda x: x[1].get(filter_name) == filter_value, values.items()))

    def validate_row(self, keyspace, table, values):
        key = f'{keyspace}/{table}'
        schema = json.loads(self.get_client().get(key)[0])
        return validate_schema(values, schema)

    def keyspace_create(self, keyspace):
        self.get_client().put_if_not_exists(keyspace, "This key is a placeholder for the keyspace".encode())

    def keyspace_delete(self, keyspace):
        self.get_client().delete_prefix(keyspace)

    def table_create(self, keyspace, table, schema):
        table_key = '{}/{}'.format(keyspace, table)
        table_value = json.dumps(schema)
        self.get_client().put_if_not_exists(table_key, table_value)

    def table_delete(self, keyspace, table):
        table_key = '{}/{}'.format(keyspace, table)
        self.get_client().delete_prefix(table_key)

    def row_create(self, keyspace, table, pk_name, pk_value, values, atomic=False, conditional=True):
        key = f'{keyspace}/{table}/{pk_value}'

        values[pk_name] = pk_value
        if self.validate_row(keyspace, table, values):
            put_response = self.get_client().put(key, json.dumps(values))
            return "SUCCESS" if put_response else "FAILURE"

        return "FAILURE"

    def row_update(self, keyspace, table, pk_name, pk_value, values, atomic=False, condition=True):
        key = f'{keyspace}/{table}/{pk_value}'

        values[pk_name] = pk_value
        client = self.get_client()
        if client.get(key) and self.validate_row(keyspace, table, values):
            put_response = client.put(key, json.dumps(values))
            return "SUCCESS" if put_response else "FAILURE"

        return "FAILURE"

    def row_read(self, keyspace, table, pk_name=None, pk_value=None):
        schema = self.get_value(f'{keyspace}/{table}')
        if pk_name and pk_value and schema["PRIMARY KEY"] == f'({pk_name})':
            key = f'{keyspace}/{table}/{pk_value}'
            return {pk_value: self.get_value(key)}

        key_prefix = f'{keyspace}/{table}/'
        return self.get_values_prefix(key_prefix, pk_name, pk_value)

    def row_delete(self, keyspace, table, pk_name, pk_value, atomic=False):
        key = f'{keyspace}/{table}/{pk_value}'
        self.get_client().delete(key)

    def row_insert_by_condition(self, keyspace, table, pk_name, pk_value, values, exists_status):
        key = f'{keyspace}/{table}/{pk_value}'
        values[pk_name] = pk_value
        exists_values = copy.deepcopy(values)
        exists_values["status"] = exists_status
        client = self.get_client()
        client.transaction(
            compare=[
                client.transactions.version(key) > 0,
            ],
            success=[
                client.transactions.put(key, json.dumps(exists_values))
            ],
            failure=[
                client.transactions.put(key, json.dumps(values))
            ]
        )

    def row_complex_field_update(self, keyspace, table, pk_name, pk_value, plan_id, updated_fields, values):
        key = f'{keyspace}/{table}/{pk_value}'
        value = self.get_value(key)
        plans = value.get('plans')
        plans.put(plan_id, updated_fields)
        value.put('plans', plans)
        self.get_client().put(key, value)

    def index_create(self, keyspace, table, index):
        # Since index is irrelevant in a KV store, this method will do nothing
        pass

    def lock_create(self, keyspace, table, pk_value):
        lock_name = f'{keyspace}.{table}.{pk_value}'
        return self.get_client().lock(lock_name)

    def lock_acquire(self, lock):
        return lock.acquire()

    def lock_delete(self, lock):
        return lock.release()
