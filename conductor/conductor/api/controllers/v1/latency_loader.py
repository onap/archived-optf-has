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

from oslo_log import log
import pecan
from pecan import expose
from conductor.api import latency_dataloader



LOG = log.getLogger(__name__)

class LatencyLoadController(object):


    def __init__(self):
        pass


    @expose(generic=True, template='json')
    def index(self):
        return 'call to get method'



    @index.when(method='POST', template='json')
    def index_POST(self, **kwargs):
        json_data = kwargs['data']
        test = latency_dataloader.LatencyDataLoader().load_into_rph(json_data)

        return kwargs['data']




pecan.route(LatencyLoadController, 'data-loader', latency_dataloader.LatencyDataLoader())