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

import os
import json
import sys

from oslo_config import cfg
from oslo_log import log

from conductor.data.plugins.file_system import base
from conductor.data.plugins.triage_translator.triage_translator import TraigeTranslator


LOG = log.getLogger(__name__)

CONF = cfg.CONF

CONFIG_OPTS = [
    cfg.IntOpt('cache_refresh_interval',
               default=1440,
               help='Interval with which to refresh the local cache, '
                    'in minutes.'),
]

CONF.register_opts(CONFIG_OPTS, group='config')


class CONFIG(base.FileSystemBase):
    """SDN Service Controller"""

    def __init__(self):
        """Initializer"""

        # FIXME(jdandrea): Pass this in to init.
        self.conf = CONF
        self.file_path = ""
        self.triage_translator=TraigeTranslator()

    def initialize(self):
        """Perform any late initialization."""
        # self.filter_candidates([])
        pass

    def get_candidates(self, demands, plan_info, triage_translator_data):
        self.triage_translator.getPlanIdNAme(plan_info['plan_name'], plan_info['plan_id'],triage_translator_data)
        resolved_demands = {}
        with open('./conductor/conductor/data/plugins/file_system/NST.json', 'r') as openfile:
            nst_object = json.load(openfile)
            for name, requirements in demands.items():
                self.triage_translator.addDemandsTriageTranslator(name, triage_translator_data)
                resolved_demands[name] = []
                for requirement in requirements:
                    inventory_type = requirement.get('inventory_type').lower()
                    if inventory_type == 'nst':#nst
                        if not nst_object or len(nst_object) < 1:
                            LOG.debug("candidtaes are B not "
                                  "available ")
                        else:
                            for region in nst_object['NST']:

                                candidate = dict()
                                candidate['inventory_provider'] = 'file_system'
                                candidate['inventory_type'] = 'NST'
                                candidate["candidate_id"] = region["NST_name"]
                                candidate['cost'] = 2
                                for key in region:
                                    candidate[key] = region[key]
                                resolved_demands[name].append(candidate)
                                LOG.debug(">>>>>>> Candidate <<<<<<<")
                                LOG.debug(json.dumps(candidate, indent=4))
            return resolved_demands





    def name(self):
        """Return human-readable name."""
        return "file_system"
