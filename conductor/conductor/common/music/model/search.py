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

"""Music ORM - Search"""

import inspect

from oslo_config import cfg
from oslo_log import log as logging

from conductor.common import db_backend

# FIXME(jdandrea): Keep for the __init__
# from conductor.common.classes import get_class

LOG = logging.getLogger(__name__)

CONF = cfg.CONF


class Query(object):
    """Data Query"""
    model = None

    def __init__(self, model):
        """Initializer"""
        if inspect.isclass(model):
            self.model = model
        # FIXME(jdandrea): Bring this back so it's path-agnostic.
        # elif isinstance(model, basestring):
        #     self.model = get_class('conductor_api.models.' + model)
        assert inspect.isclass(self.model)

    def __kwargs(self):
        """Return common keyword args"""
        kwargs = {
            'keyspace': self.model.__keyspace__,
            'table': self.model.__tablename__,  # pylint: disable=E1101
        }
        return kwargs

    def __rows_to_objects(self, rows):
        """Convert query response rows to objects"""
        results = []
        pk_name = self.model.pk_name()  # pylint: disable=E1101
        for row_id, row in rows.items():  # pylint: disable=W0612
            the_id = row.pop(pk_name)
            result = self.model(_insert=False, **row)
            setattr(result, pk_name, the_id)
            results.append(result)
        return Results(results)

    def one(self, pk_value):
        """Return object with pk_name matching pk_value"""
        pk_name = self.model.pk_name()
        kwargs = self.__kwargs()
        rows = db_backend.DB_API.row_read(
            pk_name=pk_name, pk_value=pk_value, **kwargs)
        return (self.__rows_to_objects(rows).first())

    def all(self):
        """Return all objects"""
        kwargs = self.__kwargs()
        rows = db_backend.DB_API.row_read(**kwargs)
        return self.__rows_to_objects(rows)

    def get_plan_by_col(self, pk_name, pk_value):
        # Before using this method, create an index the column (except the primary key)
        # you want to filter by.
        kwargs = self.__kwargs()
        rows = db_backend.DB_API.row_read(
            pk_name=pk_name, pk_value=pk_value, **kwargs)
        return self.__rows_to_objects(rows)

    def filter_by(self, **kwargs):
        """Filter objects"""
        # Music doesn't allow filtering on anything but the primary key.
        # We need to get all items and then go looking for what we want.
        all_items = self.all()
        filtered_items = Results([])
        # For every candidate ...
        for item in all_items:
            passes = True
            # All filters are AND-ed.
            for key, value in kwargs.items():
                if getattr(item, key) != value:
                    passes = False
                    break
            if passes:
                filtered_items.append(item)
        return filtered_items

    def first(self):
        """Return first object"""
        return self.all().first()


class Results(list):
    """Query results"""

    def __init__(self, *args, **kwargs):  # pylint: disable=W0613
        """Initializer"""
        super(Results, self).__init__(args[0])

    def all(self):
        """Return all"""
        return self

    def first(self):
        """Return first"""
        if len(self) > 0:
            return self[0]
