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

"""Music ORM - Model"""

from abc import ABCMeta
from abc import abstractmethod
import uuid

from oslo_config import cfg
from oslo_log import log as logging
import six

from conductor.common.classes import abstractclassmethod
from conductor.common.classes import classproperty
from conductor.common import db_backend
from conductor.common.music.model import search

LOG = logging.getLogger(__name__)

CONF = cfg.CONF


@six.add_metaclass(ABCMeta)
class Base(object):
    """A custom declarative base ORM-style class.

    Provides some Elixir-inspired shortcuts as well.
    """

    # These must be set in the derived class!
    __tablename__ = None
    __keyspace__ = None

    @classproperty
    def query(cls):  # pylint: disable=E0213
        """Return a query object a la sqlalchemy"""
        return search.Query(cls)

    @classmethod
    def __kwargs(cls):
        """Return common keyword args"""
        kwargs = {
            'keyspace': cls.__keyspace__,
            'table': cls.__tablename__,
        }
        return kwargs

    @classmethod
    def table_create(cls):
        """Create table"""
        kwargs = cls.__kwargs()
        kwargs['schema'] = cls.schema()
        db_backend.DB_API.table_create(**kwargs)

        # Create indexes for the table
        del kwargs['schema']
        if cls.indexes():
            for index in cls.indexes():
                kwargs['index'] = index
                db_backend.DB_API.index_create(**kwargs)

    @abstractclassmethod
    def atomic(cls):
        """Use atomic operations"""
        return False

    @abstractclassmethod
    def schema(cls):
        """Return schema"""
        return cls()

    @classmethod
    def indexes(cls):
        """Return Indexes"""
        pass
        # return cls()

    @abstractclassmethod
    def pk_name(cls):
        """Primary key name"""
        return cls()

    @abstractmethod
    def pk_value(self):
        """Primary key value"""
        pass

    @abstractmethod
    def values(self):
        """Values"""
        pass

    def insert(self):
        """Insert row"""
        kwargs = self.__kwargs()
        kwargs['pk_name'] = self.pk_name()
        kwargs['values'] = self.values()
        kwargs['atomic'] = self.atomic()
        pk_name = kwargs['pk_name']

        if pk_name not in kwargs['values']:
            # TODO(jdandrea): Make uuid4() generation a default method in Base.
            the_id = str(uuid.uuid4())
            kwargs['values'][pk_name] = the_id
            kwargs['pk_value'] = the_id
            setattr(self, pk_name, the_id)
        else:
            kwargs['pk_value'] = kwargs['values'][pk_name]
        response = db_backend.DB_API.row_create(**kwargs)
        return response

    def update(self, condition=None):
        """Update row"""
        kwargs = self.__kwargs()
        kwargs['pk_name'] = self.pk_name()
        kwargs['pk_value'] = self.pk_value()
        kwargs['values'] = self.values()

        # In active-active, all update operations should be atomic
        kwargs['atomic'] = True
        kwargs['condition'] = condition
        # FIXME(jdandrea): Do we need this test/pop clause?
        pk_name = kwargs['pk_name']
        if kwargs['table'] != ('order_locks'):
            if pk_name in kwargs['values']:
                kwargs['values'].pop(pk_name)
        return db_backend.DB_API.row_update(**kwargs)

    def delete(self):
        """Delete row"""
        kwargs = self.__kwargs()
        kwargs['pk_name'] = self.pk_name()
        kwargs['pk_value'] = self.pk_value()
        kwargs['atomic'] = self.atomic()
        db_backend.DB_API.row_delete(**kwargs)

    @classmethod
    def filter_by(cls, **kwargs):
        """Filter objects"""
        return cls.query.filter_by(**kwargs)  # pylint: disable=E1101

    def flush(self, *args, **kwargs):
        """Flush changes to storage"""
        # TODO(jdandrea): Implement in music? May be a no-op
        pass

    def as_dict(self):
        """Return object representation as a dictionary"""
        return dict((k, v) for k, v in self.__dict__.items()
                    if not k.startswith('_'))


def create_dynamic_model(keyspace, classname, baseclass):
    """Create a dynamic ORM class with a custom keyspace/class/table.

    Given a keyspace, a camelcase class name, and a base class
    derived from Base, create a dynamic model that adopts a
    table name based on a lower-cased version of the class name,
    then create the table in the keyspace if it doesn't already exist.
    If the baseclass already has __tablename__ or __keyspace__ set, those
    will take precedence. Set those to None to use keyspace/classname here.
    """

    # The comma after baseclass belongs there! Tuple of length 1.
    model = type(
        classname, (baseclass,), {
            '__tablename__': baseclass.__tablename__ or classname.lower(),
            '__keyspace__': baseclass.__keyspace__ or keyspace})
    model.table_create()
    return model
