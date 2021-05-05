#
# -------------------------------------------------------------------------
#   Copyright (c) 2015-2018 AT&T Intellectual Property
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

import json
import logging

from conductor.common import db_backend


class LoggerFilter(logging.Filter):
    transaction_id = None
    plan_id = None

    def filter(self, record):
        record.transaction_id = self.transaction_id
        record.plan_id = self.plan_id
        return True


def getTransactionId(keyspace, plan_id):
    """get transaction id from a pariticular plan in MUSIC """

    rows = db_backend.get_client().row_read(keyspace, "plans", "id", plan_id)
    if 'result' in rows:
        rows = rows['result']
    for row_id, row_value in rows.items():
        template = row_value['template']
        if template:
            data = json.loads(template)
            if "transaction-id" in data:
                return data["transaction-id"]


def setLoggerFilter(logger, keyspace, plan_id):

    generic_formatter = logging.Formatter('%(asctime)s|%(transaction_id)s|%(thread)d|%(levelname)s|%(module)s|%('
                                          'name)s: '
                                          ' [-] plan id: %(plan_id)s [-] %(message)s')
    audit_formatter = logging.Formatter('%(asctime)s|%(asctime)s|%(transaction_id)s||%('
                                        'thread)d||Conductor|N/A|COMPLETE '
                                        '|200|sucessful||%(levelname)s|||0|%(module)s|||||||||%(name)s : [-] '
                                        'plan id: %(plan_id)s [-] %(message)s')
    metric_formatter = logging.Formatter('%(asctime)s|%(asctime)s|%(transaction_id)s||%('
                                         'thread)d||Conductor|N/A|N/A|N/A| '
                                         'COMPLETE|200|sucessful||%(levelname)s|||0|%(module)s||||||||||%(name)s : ['
                                         '-] '
                                         'plan id: %(plan_id)s [-] %(message)s')
    error_formatter = logging.Formatter('%(asctime)s|%(transaction_id)s|%(thread)d|Conductor|N/A|N/A|N/A|ERROR|500'
                                        '|N/A|%(name)s : [-] plan id: %(plan_id)s [-] %(message)s')

    logger_filter = LoggerFilter()
    logger_filter.transaction_id = getTransactionId(keyspace, plan_id)
    logger_filter.plan_id = plan_id

    for handler in logger.logger.parent.handlers:
        if hasattr(handler, 'baseFilename') and "audit" in handler.baseFilename:
            handler.setFormatter(audit_formatter)
        elif hasattr(handler, 'baseFilename') and "metric" in handler.baseFilename:
            handler.setFormatter(metric_formatter)
        elif hasattr(handler, 'baseFilename') and "error" in handler.baseFilename:
            handler.setFormatter(error_formatter)
        else:
            handler.setFormatter(generic_formatter)
        handler.addFilter(logger_filter)
