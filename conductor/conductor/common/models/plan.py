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

"""Plan Model"""

import json
import time

from conductor.common.models import validate_uuid4
from conductor.common.music.model import base


def current_time_millis():
    """Current time in milliseconds."""
    return int(round(time.time() * 1000))


class Plan(base.Base):
    """Plan model.

    DO NOT use this class directly!

    Only create Plan-based classes using:
    base.create_dynamic_model(keyspace=KEYSPACE,
        baseclass=Plan, classname=CLASS).
    The table will be automatically created if it doesn't exist.
    """

    __tablename__ = "plans"
    __keyspace__ = None

    id = None  # pylint: disable=C0103
    status = None
    created = None
    updated = None
    name = None
    timeout = None
    recommend_max = None
    message = None
    template = None
    translation = None
    solution = None

    # Status
    TEMPLATE = "template"  # Template ready for translation
    TRANSLATED = "translated"  # Translation ready for solving
    SOLVING = "solving"  # Search for solutions in progress
    # Search complete, solution with n>0 recommendations found
    SOLVED = "solved"
    # Search failed, no recommendations found
    NOT_FOUND = "not found"
    ERROR = "error"  # Error
    # Solved, but reservation of resources in progress
    RESERVING = "reserving"
    # Final state, Solved and Reserved resources (if required)
    DONE = "done"
    STATUS = [TEMPLATE, TRANSLATED, SOLVING, SOLVED, NOT_FOUND,
              ERROR, RESERVING, DONE, ]
    WORKING = [TEMPLATE, TRANSLATED, SOLVING, RESERVING, ]
    FINISHED = [SOLVED, NOT_FOUND, ERROR, DONE, ]

    @classmethod
    def schema(cls):
        """Return schema."""
        schema = {
            'id': 'text',  # Plan ID in UUID4 format
            'status': 'text',  # Plan status (see STATUS for valid values)
            'created': 'bigint',  # Creation time in msec from epoch
            'updated': 'bigint',  # Last update time in msec from epoch
            'name': 'text',  # Plan name/alias
            'timeout': 'int',  # Timeout in seconds
            'recommend_max': 'int',  # Max recommendations
            'message': 'text',  # Message (e.g., error or other info)
            'template': 'text',  # Plan template
            'translation': 'text',  # Translated template for the solver
            'solution': 'text',  # The (ocean is the ultimate) solution (FZ)
            'PRIMARY KEY': '(id)',
        }
        return schema

    @classmethod
    def atomic(cls):
        """Use atomic operations"""
        return False

    @classmethod
    def pk_name(cls):
        """Primary key name"""
        return 'id'

    def pk_value(self):
        """Primary key value"""
        return self.id

    @property
    def error(self):
        return self.status == self.ERROR

    @property
    def finished(self):
        return self.status in self.FINISHED

    @property
    def solved(self):
        return self.status == self.SOLUTION

    @property
    def done(self):
        return self.status == self.DONE

    @property
    def timedout(self):
        """Calculate if a plan has timed out"""
        elapsed_msec = (current_time_millis() - self.created)
        return elapsed_msec >= self.timeout * 1000

    @property
    def working(self):
        return self.status in self.WORKING

    def update(self):
        """Update plan

        Side-effect: Sets the updated field to the current time.
        """
        self.updated = current_time_millis()
        super(Plan, self).update()

    def values(self):
        """Values"""
        value_dict = {
            'status': self.status,
            'created': self.created,
            'updated': self.updated,
            'name': self.name,
            'timeout': self.timeout,
            'recommend_max': self.recommend_max,
            'message': self.message,
            'template': json.dumps(self.template),
            'translation': json.dumps(self.translation),
            'solution': json.dumps(self.solution),
        }
        if self.id:
            value_dict['id'] = self.id
        return value_dict

    def __init__(self, name, timeout, recommend_max, template,
                 id=None, created=None, updated=None, status=None,
                 message=None, translation=None, solution=None, _insert=True):
        """Initializer"""
        super(Plan, self).__init__()
        self.status = status or self.TEMPLATE
        self.created = created or current_time_millis()
        self.updated = updated or current_time_millis()
        self.name = name
        self.timeout = timeout
        self.recommend_max = recommend_max
        self.message = message or ""
        if _insert:
            if validate_uuid4(id):
                self.id = id
            self.template = template or {}
            self.translation = translation or {}
            self.solution = solution or {}
            self.insert()
        else:
            self.template = json.loads(template)
            self.translation = json.loads(translation)
            self.solution = json.loads(solution)

    def __repr__(self):
        """Object representation"""
        return '<Plan {} ({})>'.format(self.name, self.id)

    def __json__(self):
        """JSON representation"""
        json_ = {}
        json_['id'] = self.id
        json_['status'] = self.status
        json_['created'] = self.created
        json_['updated'] = self.updated
        json_['name'] = self.name
        json_['timeout'] = self.timeout
        json_['recommend_max'] = self.recommend_max
        json_['message'] = self.message
        json_['template'] = self.template
        json_['translation'] = self.translation
        json_['solution'] = self.solution
        return json_
