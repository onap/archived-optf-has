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

"""Music ORM - Transactions"""

from oslo_log import log as logging

LOG = logging.getLogger(__name__)


def start():
    """Start transaction"""
    pass


def start_read_only():
    """Start read-only transaction"""
    start()


def commit():
    """Commit transaction"""
    pass


def rollback():
    """Rollback transaction"""
    pass


def clear():
    """Clear transaction"""
    pass


def flush():
    """Flush to disk"""
    pass
