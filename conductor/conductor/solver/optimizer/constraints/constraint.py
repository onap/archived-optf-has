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

import abc

from oslo_log import log
import six

LOG = log.getLogger(__name__)


@six.add_metaclass(abc.ABCMeta)
class Constraint(object):
    """Base class for Constraints"""

    def __init__(self, _name, _type, _demand_list, _priority=0):
        """Common initializer.

        Be sure to call this superclass when initializing.
        """
        self.name = _name
        self.constraint_type = _type
        self.demand_list = _demand_list
        self.check_priority = _priority

    @abc.abstractmethod
    def solve(self, _decision_path, _candidate_list, _request):
        """Solve.

        Implement the constraint solving in each inherited class,
        depending on constraint type.
        """

        return _candidate_list
