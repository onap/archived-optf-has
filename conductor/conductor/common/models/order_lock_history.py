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
import time
from conductor.common.models import validate_uuid4
from conductor.common.music.model import base
from conductor.common.music import api

class OrderLockHistory(base.Base):

    __tablename__ = "order_locks_history"
    __keyspace__ = None

    id = None
    conflict_id = None
    plans = None
    is_spinup_completed = None
    spinup_completed_timestamp = None

    # Status
    PARKED = "parked"
    UNDER_SPIN_UP = "under-spin-up"
    COMPLETED = "completed"
    REHOME = "rehome"
    FAILED = "failed"

    SPINING = [PARKED, UNDER_SPIN_UP]
    REHOMABLE = [REHOME, COMPLETED]

    @classmethod
    def schema(cls):
        """Return schema."""
        schema = {
            'id': 'text',
            'conflict_id': 'text',
            'plans': 'map<text, text>',
            'is_spinup_completed': 'boolean',
            'spinup_completed_timestamp': 'bigint',
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
            'conflict_id' : self.conflict_id,
            'plans': self.plans,
            'is_spinup_completed': self.is_spinup_completed,
            'spinup_completed_timestamp': self.spinup_completed_timestamp
        }
        if self.id:
            value_dict['id'] = self.id
        return value_dict

    def __init__(self, id=None, conflict_id=None, plans=None, is_spinup_completed=False, spinup_completed_timestamp=None, _insert=False):
        """Initializer"""
        super(OrderLockHistory, self).__init__()
        # Breaking here with errot: Can't set attribute (TODO: Ikram/Rupali)
        self.conflict_id = conflict_id
        self.plans = plans
        self.is_spinup_completed = is_spinup_completed
        self.spinup_completed_timestamp = spinup_completed_timestamp

        if _insert:
            self.insert()

    def __repr__(self):
        """Object representation"""
        return '<OrderLock {}>'.format(self.id)

    def __json__(self):
        """JSON representation"""
        json_ = {}
        json_[id] = self.id,
        json_['conflict_id'] = self.conflict_id
        json_['plans'] = self.plans
        json_['is_spinup_completed'] = self.is_spinup_completed
        json_['spinup_completed_timestamp'] = self.spinup_completed_timestamp

        return json_
