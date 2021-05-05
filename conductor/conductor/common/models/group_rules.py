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

from conductor.common import db_backend
from conductor.common.music.model import base


class GroupRules(base.Base):

    __tablename__ = "group_rules"
    __keyspace__ = None

    id = None
    group = None
    rule = None

    # Status
    PARKED = "parked"
    UNDER_SPIN_UP = "under-spin-up"
    COMPLETED = "completed"
    REHOME = "rehome"
    FAILED = "failed"

    @classmethod
    def schema(cls):
        """Return schema."""
        schema = {
            'id': 'text',
            'group': 'text',
            'rule': 'map<text,text>',
            'PRIMARY KEY': '(id)'
        }
        return schema

    @classmethod
    def atomic(cls):
        """Use atomic operations"""
        return True

    @classmethod
    def pk_name(cls):
        """Primary key name"""
        return 'id'

    def pk_value(self):
        """Primary key value"""
        return self.id

    def values(self):
        """Valu-es"""
        value_dict = {
            'id': self.id,
            'group': self.group
        }
        return value_dict

    def update(self, group, updated_fields):
        """Update country latency"""
        db_backend.DB_API.row_complex_field_update(
            self.__keyspace__, self.__tablename__, self.pk_name(),
            self.pk_value(), group, updated_fields)

    def insert(self):
        return \
            db_backend.DB_API.row_insert_by_condition(
                self.__keyspace__, self.__tablename__, self.pk_name(),
                self.pk_value(), self.values(), self.PARKED
            )

    def __init__(self, id=None, group=None, rule=None, _insert=False):
        """Initializer"""
        super(GroupRules, self).__init__()

        self.id = id
        self.group = group
        self.rule = rule

        if _insert:
            self.insert()

    def __repr__(self):
        """Object representation"""
        return '<GroupRules {}>'.format(self.id)

    def __json__(self):
        """JSON representation"""
        json_ = {}
        json_[id] = self.id,
        json_['group'] = self.group,
        json_['rule'] = self.rule

        return json_
