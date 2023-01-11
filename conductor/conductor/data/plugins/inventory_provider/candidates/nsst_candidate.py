#
# -------------------------------------------------------------------------
#   Copyright (C) 2022 Deutsche telekom AG.
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


class NSST(Candidate):
    def __init__(self, **kwargs):
        super().__init__(kwargs['info'])
        self.nsst_info = kwargs['model_info']
        self.model_ver_info = kwargs['model_ver']
        self.profile_info = kwargs['profile_info']
        self.other = kwargs['default_fields']

