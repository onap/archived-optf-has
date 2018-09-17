#
# -------------------------------------------------------------------------
#   Copyright (c) 2015-2017 AT&T Intellectual Property
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
from conductor.common.music.model import base


class TriageTool(base.Base):
    __tablename__ = "triage_tool"
    __keyspace__ = None
    id =None
    name = None
    optimization_type = None
    triage_solver = None
    triage_translator = None
    @classmethod
    def schema(cls):
        schema = {
            'id': 'text',
            'name': 'text',
            "optimization_type" : 'text',
            'triage_solver': 'text',
            'triage_translator': 'text',
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
            'name': self.name,
            'optimization_type' : self.optimization_type,
            'triage_translator': json.dumps(self.triage_translator),
            'triage_solver': json.dumps(self.triage_solver)
        }
        return value_dict

    def __init__(self, id=None, name=None, optimization_type=None, triage_solver=None, triage_translator=None, _insert=False):

        super(TriageTool, self).__init__()
        self.id = id
        self.optimization_type = optimization_type
        #self.triage_solver = triage_solver
        #self.triage_translator = triage_translator
        self.name = name
        if triage_solver is not None:
            self.triage_solver = json.loads(triage_solver)
        else:
            self.triage_solver = triage_solver
        if triage_translator is not None:
            self.triage_translator = json.loads(triage_translator)
        else:
            self.triage_translator = triage_translator
        # if _insert:
        #    self.insert()

    def __repr__(self):
        """Object representation"""
        return '<Triage Tool {}>'.format(self.id)

    def __json__(self):
        """JSON representation"""
        json_ = {}
        json_[id] = self.id,
        json_['optimization_type'] = self.optimization_type,
        json_['triage_solver'] = self.triage_solver,
        json_['triage_translator'] = self.triage_translator,
        json_['name'] = self.name

        return json_
