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

from oslo_log import log

from conductor.solver.optimizer import decision_path as dpath
from conductor.solver.optimizer import search
from random import randint

LOG = log.getLogger(__name__)


class RandomPick(search.Search):
    def __init__(self, conf):
        search.Search.__init__(self, conf)

    def search(self, _demand_list, _request):
        decision_path = dpath.DecisionPath()
        decision_path.set_decisions({})
        return self._find_current_best(_demand_list, decision_path, _request)

    def _find_current_best(self, _demand_list, _decision_path, _request):
        for demand in _demand_list:
            r_index = randint(0, len(demand.resources) - 1)
            best_resource = demand.resources[demand.resources.keys()[r_index]]
            _decision_path.decisions[demand.name] = best_resource
        return _decision_path
