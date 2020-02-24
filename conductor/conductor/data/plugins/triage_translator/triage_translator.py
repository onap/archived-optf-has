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

import copy
import json

from conductor.common.models.triage_tool import TriageTool
from conductor.common.music.model import base
from oslo_config import cfg
try:
    from StringIO import StringIO ## for Python 2
except ImportError:
    from io import StringIO ## for Python 3


CONF = cfg.CONF
io = StringIO()


class TraigeTranslator(object):


    def getPlanIdNAme(self, plan_name, plan_id, triage_translator_data):
        triage_translator_data['plan_name'] = plan_name
        triage_translator_data['plan_id'] = plan_id
    def addDemandsTriageTranslator(self, name, triage_translator_data):
        if not 'dropped_candidates' in list(triage_translator_data.keys()):
            triage_translator_data['dropped_candidates'] = []
            dropped_candidate_details = {}
            dropped_candidate_details['name'] = name
            dropped_candidate_details['translation_dropped'] = []
            dropped_candidate_details['latency_dropped'] = []
            triage_translator_data['dropped_candidates'].append(dropped_candidate_details)
        else:
            for dc in triage_translator_data['dropped_candidates']:
                print(name)   # Python 3 conversion as print statement changed from python 2
                if not dc['name'] == name:
                    dropped_candidate_details = {}
                    dropped_candidate_details['name'] = name
                    dropped_candidate_details['translation_dropped'] = []
                    triage_translator_data['dropped_candidates'].append(dropped_candidate_details)

    def collectDroppedCandiate(self, candidate_id, location_id, name, triage_translator_data, reason):
        drop_can = {}
        drop_can['candidate_id'] = candidate_id
        if drop_can['candidate_id'] == "null":
            drop_can['candidate_id']= None
        drop_can['location_id'] = location_id
        drop_can['reason'] = reason
        for dropped_c in triage_translator_data['dropped_candidates']:
            if dropped_c['name'] == name:
                dropped_c['translation_dropped'].append(drop_can)

    def thefinalCallTrans(self, triage_translator_data):
        triage_translator = {}
        triage_translator['plan_id'] = triage_translator_data['plan_id']
        triage_translator['plan_name'] = triage_translator_data['plan_name']
        triage_translator['translator_triage']= {}
        triage_translator['translator_triage']['dropped_candidates'] = []

        for td in triage_translator_data['translator_triage']:
            for a in td:
                triage_translator['translator_triage']['dropped_candidates'].append(a)
        tria_final = triage_translator['translator_triage']
        triage_translator_dataTool = base.create_dynamic_model(
            keyspace=CONF.keyspace, baseclass=TriageTool, classname="TriageTool")

        triage_translator = json.dumps(tria_final )
        triageTransDatarow = triage_translator_dataTool(id=triage_translator_data['plan_id'], name=triage_translator_data['plan_name'],
                                             triage_translator=triage_translator)
        response = triageTransDatarow.insert()


