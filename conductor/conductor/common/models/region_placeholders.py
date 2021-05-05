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


class RegionPlaceholders(base.Base):

    __tablename__ = "region_placeholders"
    __keyspace__ = None

    id = None
    region_name = None
    countries = None

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
            'region_name': 'text',
            'countries': 'map<text,text>',
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
            'region_name': self.region_name,
            'countries': self.countries
        }
        if self.id:
            value_dict['id'] = self.id
        return value_dict

    def delete(self, region_id):
        """Update country latency"""
        return db_backend.DB_API.row_delete(self.__keyspace__, self.__tablename__, self.pk_name(),
                                            region_id, True)

    def update(self, region_name, updated_fields):
        """Update country latency"""
        db_backend.DB_API.row_complex_field_update(
            self.__keyspace__, self.__tablename__, self.pk_name(),
            self.pk_value(), region_name, updated_fields)

    def __init__(self, region_name=None, countries=None, _insert=False):
        """Initializer"""
        super(RegionPlaceholders, self).__init__()
        self.region_name = region_name
        self.countries = countries

    def __repr__(self):
        """Object representation"""
        return '<RegionPlaceholders {}>'.format(self.id)

    def __json__(self):
        """JSON representation"""
        json_ = {}
        json_[id] = self.id,
        json_['region_name'] = self.region_name
        json_['countries'] = self.countries

        return json_
