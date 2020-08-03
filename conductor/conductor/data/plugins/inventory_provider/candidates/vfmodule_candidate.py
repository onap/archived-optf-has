#
# -------------------------------------------------------------------------
#   Copyright (C) 2020 Wipro Limited.
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


from conductor.data.plugins.inventory_provider.candidates.candidate import Candidate


class VfModule(Candidate):
    def __init__(self,**kwargs):
        super().__init__(kwargs['info'])
        self.generic_vnf = kwargs['generic_vnf']
        self.cloud_region = kwargs['cloud_region']
        self.service_instance = kwargs['service_instance']
        self.vf_module = kwargs['vf_module']
        self.vserver = kwargs['vserver']
        self.complex = kwargs['complex']
        self.vlan = kwargs['vlan']
        self.additional_fields = kwargs['additional_fields']