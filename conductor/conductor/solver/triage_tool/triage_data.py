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
    from StringIO import StringIO
except ImportError:
    from io import StringIO


CONF = cfg.CONF
io = StringIO()
class TriageData(object):
    def __init__(self):
        self.TriageTool = base.create_dynamic_model(
            keyspace=CONF.keyspace, baseclass=TriageTool, classname="TriageTool")

        self.triage = {}

        self.triage['candidates'] = []
        self.triage['final_candidate']= {}
        self.children = {'children' :[]}
        self.triage['plan_id'] = None
        self.triage['request_id'] = None
        self.sorted_demand = []

    def getSortedDemand(self, sorted_demand):
        for d in sorted_demand:
            if not d.name in self.sorted_demand:
                # print d.name
                self.sorted_demand.append(d.name)
        self.sorted_demand

    def aasignNodeIdToCandidate(self, candiate, current_demand, request, plan_id):
        demand_name = current_demand.name
        self.triage['plan_id'] = plan_id
        self.triage['request_id'] = request
        candidateCopyStructure = []
        candidateCopy = copy.copy(candiate)
        for cs in candidateCopy:
            candidate_stru = {}
            # candidate_stru['complex_name'] = cs['complex_name']
            # candidate_stru['inventory_type'] = cs['inventory_type']
            # candidate_stru['candidate_id'] = cs['candidate_id']
            # candidate_stru['physical_location_id'] = cs['physical_location_id']
            # candidate_stru['location_id'] = cs['location_id']
            candidate_stru['node_id'] = cs['node_id']
            candidate_stru['constraints'] =cs['constraints']
            candidate_stru['name'] = cs['name']
            candidateCopyStructure.append(candidate_stru)
        for cr in candidateCopyStructure:
            if not cr in self.triage['candidates']:
                for c in current_demand.constraint_list:
                    constraint = {}
                    constraint['name'] = c.name
                    constraint['status'] = None
                    constraint['constraint_type'] = c.constraint_type
                    cr['constraints'].append(constraint)
                self.triage['candidates'].append(cr)


    def checkCandidateAfter(self,solver):
        for ca in solver['candidate_after_list']:
            for resource_candidate in self.triage['candidates']:
                if ca['node_id'] == resource_candidate['node_id']:
                    for rcl in resource_candidate['constraints']:
                        if (rcl['name'] == solver['constraint_name_for_can']):
                            rcl['status'] = "passed"
        return self.triage

    def droppedCadidatesStatus(self, dropped_candidate):
        for dc in dropped_candidate:
            for ca in self.triage['candidates']:
                if dc['node_id'] == ca['node_id']:
                    ca['type'] ='dropped'
                    for cca in ca['constraints']:
                        for dl in dc['constraints']:
                            if 'constraint_name_dropped' in list(dl.keys()):    # Python 3 Conversion -- dict object to list object
                                if(cca['name'] == dl['constraint_name_dropped']):
                                    dc['status'] = "dropped"
        return self.triage

    def rollBackStatus(self, demanHadNoCandidate, decisionWeneedtoRollback):
        if len(decisionWeneedtoRollback.decisions) >0:
            count = self.sorted_demand.index(demanHadNoCandidate.name)
            count = count-1
            if count == 0:
                decision_rolba = list(decisionWeneedtoRollback.decisions.values())   # Python 3 Conversion -- dict object to list object
                for x in decision_rolba:
                    for canrb in self.triage['candidates']:
                        if x['node_id'] == canrb['node_id'] :
                            canrb['type'] = "rollback"
                            # The folloing print statement was missing a test case - run tox to see
                            #print x['node_id'], ' +++ ', canrb['node_id']
                            children = []
                            for childCand in self.triage['candidates']:
                                if demanHadNoCandidate.name == childCand['name']:
                                    children.append(childCand)
                            canrb['children'] = children

            elif len(decisionWeneedtoRollback.decisions) == 0:
                self.triage['name'] = demanHadNoCandidate.name
                self.triage['message'] = "this is parent demand and has no resource to rollback "
            else:
                decision_rolba = decisionWeneedtoRollback.decisions
                #print decision_rolba[count]
                candRollBack = decision_rolba[count]
                for resource_rollback in self.triage['candidates']:
                    if candRollBack['node_id'] == resource_rollback['node_id']:
                        resource_rollback['type'] = "rollback"


    def getSolution(self, decision_list):

        if len(decision_list) == 0:
            self.children['children']=(self.triage['candidates'])
            self.triage['final_candidate']= self.children
            triaP = json.dumps(self.triage['final_candidate'])
        else:
            self.triage['candidates'] = [i for n, i in enumerate(self.triage['candidates']) if i not in self.triage['candidates'][n+1:]]

            counter = 0
            d1 = []; d2 = []; d3 = []; d4 = []; d5 = []; d6 = []
            for fc in decision_list:
                for final_cand in list(fc.values()):   # Python 3 Conversion -- dict object to list object
                    for final_resou in self.triage['candidates']:
                        if final_cand['node_id'] == final_resou['node_id']:
                            if 'type' in list(final_resou.keys()) :    # Python 3 Conversion -- dict object to list object
                                if not final_resou['type'] == "dropped":
                                    final_resou['type'] = 'solution'
                                    final_resou['children'] = []
                            else:
                                final_resou['type'] = 'solution'
                                final_resou['children'] = []

                        elif not 'type' in list(final_resou.keys()):    # Python 3 Conversion -- dict object to list object
                            final_resou['type'] = 'not tried'
            #
            for cand in self.triage['candidates']:
                if cand['name'] == self.sorted_demand[0]:
                    d1.append(cand)
                elif cand['name'] == self.sorted_demand[1]:
                    d2.append(cand)
                elif self.sorted_demand[2] == cand['name']:
                    d3.append(cand)
                elif self.sorted_demand[3] == cand['name']:
                    d4.append(cand)
                elif self.sorted_demand[4] == cand['name']:
                    d5.append(cand)
                elif self.sorted_demand[5] == cand['name']:
                    d6.append(cand)
                else:
                    break
            if len(d1) > 0:
                for d1c in d1:
                    if d1c['type'] == 'solution':
                        d1c['children'] = (d2)
                        if len(d1c['children']) == 0:
                            break
                        else:
                            for d2c in d1c['children']:
                                if d2c['type'] == 'solution':
                                    d2c['children'] = (d3)
                                    if len(d2c['children']) == 0:
                                        break
                                    else:
                                        for d3c in d2c['children']:
                                            if d3c['type'] == 'solution':
                                                d3c['children'] = (d4)
                                                if len(d3c['children']) == 0:
                                                    break
                                                else:
                                                    for d4c in d3c['children']:
                                                        if d4c['type'] == 'solution':
                                                            d4c['children'] = (d5)
                                                            if len(d4c['children']) == 0:
                                                                break
                                                            else:
                                                                for d5c in d4c['children']:
                                                                    if d5c['type'] == 'solution':
                                                                        d5c['children'] = (d6)


                self.children['children']=(d1)
                self.triage['final_candidate'] = self.children
            triaP = json.dumps(self.triage['final_candidate'])
        triageRowUpdate = self.TriageTool.query.get_plan_by_col("id", self.triage['plan_id'])[0]
        triageRowUpdate.triage_solver = triaP
        triageRowUpdate.update()
        # triageDatarow = self.TriageTool(id=self.triage['plan_id'], name=self.triage['request_id'],
        #                                 triage_solver=triaP)
        # response = triageDatarow.insert()









