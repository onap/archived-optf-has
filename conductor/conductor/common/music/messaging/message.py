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

"""Message Model"""

import json
import time

from conductor.common.music.model import base


def current_time_millis():
    """Current time in milliseconds."""
    return int(round(time.time() * 1000))


class Message(base.Base):
    """Message model.

    DO NOT use this class directly! With messaging, the table
    name must be the message topic, thus this class has a
    __tablename__ and __keyspace__ of None.

    Only create Message-based classes using:
    base.create_dynamic_model(keyspace=KEYSPACE,
        baseclass=Message, classname=TOPIC_NAME).
    The table will be automatically created if it doesn't exist.
    """

    __tablename__ = None
    __keyspace__ = None

    id = None  # pylint: disable=C0103
    action = None
    created = None
    updated = None
    ctxt = None
    method = None
    args = None
    status = None
    owner = None
    response = None
    failure = None

    # Actions
    CALL = "call"
    CAST = "cast"
    ACTIONS = [CALL, CAST, ]

    # Status
    ENQUEUED = "enqueued"
    WORKING = "working"
    COMPLETED = "completed"
    ERROR = "error"
    STATUS = [ENQUEUED, WORKING, COMPLETED, ERROR, ]
    FINISHED = [COMPLETED, ERROR, ]

    @classmethod
    def schema(cls):
        """Return schema."""
        schema = {
            'id': 'text',  # Message ID in UUID4 format
            'action': 'text',  # Message type (call, cast)
            'created': 'bigint',  # Creation time in msec from epoch
            'updated': 'bigint',  # Last update time in msec from epoch
            'ctxt': 'text',  # JSON request context dictionary
            'method': 'text',  # RPC method name
            'args': 'text',  # JSON argument dictionary
            'status': 'text',  # Status (enqueued, complete, error)
            'owner': 'text',
            'response': 'text',  # Response JSON
            'failure': 'text',  # Failure JSON (used for exceptions)
            'PRIMARY KEY': '(id)',
        }
        return schema

    @classmethod
    def atomic(cls):
        """Use atomic operations"""
        return False  # FIXME: this should be True for atomic operations

    @classmethod
    def pk_name(cls):
        """Primary key name"""
        return 'id'

    def pk_value(self):
        """Primary key value"""
        return self.id

    @property
    def enqueued(self):
        return self.status == self.ENQUEUED

    @property
    def working(self):
        return self.status == self.WORKING

    @property
    def finished(self):
        return self.status in self.FINISHED

    @property
    def ok(self):
        return self.status == self.COMPLETED

    def update(self, condition=None):
        """Update message

        Side-effect: Sets the updated field to the current time.
        """
        self.updated = current_time_millis()
        return super(Message, self).update(condition)

    def values(self):
        """Values"""
        return {
            'action': self.action,
            'created': self.created,
            'updated': self.updated,
            'ctxt': json.dumps(self.ctxt),
            'method': self.method,
            'args': json.dumps(self.args),
            'status': self.status,
            'owner': self.owner,
            'response': json.dumps(self.response),
            'failure': self.failure,  # already serialized by oslo_messaging
        }

    def __init__(self, action, ctxt, method, args,
                 created=None, updated=None, status=None,
                 response=None, owner=None, failure=None, _insert=True):
        """Initializer"""
        super(Message, self).__init__()
        self.action = action
        self.created = created or current_time_millis()
        self.updated = updated or current_time_millis()
        self.method = method
        self.owner = owner or {}
        self.status = status or self.ENQUEUED
        if _insert:
            self.ctxt = ctxt or {}
            self.args = args or {}
            self.response = response or {}
            self.failure = failure or ""
            self.insert()
        else:
            self.ctxt = json.loads(ctxt)
            self.args = json.loads(args)
            self.response = json.loads(response)
            self.failure = failure  # oslo_messaging will deserialize this

    def __repr__(self):
        """Object representation"""
        return '<Message Topic %r>' % self.__tablename__

    def __json__(self):
        """JSON representation"""
        json_ = {}
        json_['id'] = self.id
        json_['action'] = self.action
        # TODO(jdandrea): Format timestamps as ISO
        json_['created'] = self.created
        json_['updated'] = self.updated
        json_['ctxt'] = self.ctxt
        json_['method'] = self.method
        json_['args'] = self.args
        json_['status'] = self.status
        json_['owner'] = self.owner
        json_['response'] = self.response
        json_['failure'] = self.failure
        return json_
