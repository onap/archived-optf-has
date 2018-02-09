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

import pecan

from conductor.api.controllers import errors
from conductor.api.controllers.v1 import root as v1

MEDIA_TYPE_JSON = 'application/vnd.onap.has-%s+json'


class RootController(object):
    """Root Controller /"""

    def __init__(self):
        self.errors = errors.ErrorsController()
        self.v1 = v1.V1Controller()

    @pecan.expose(generic=True, template='json')
    def index(self):
        """Catchall for all methods"""
        base_url = pecan.request.application_url
        available = [{'tag': 'v1', 'date': '2016-11-01T00:00:00Z', }]
        collected = [version_descriptor(base_url, v['tag'], v['date'])
                     for v in available]
        versions = {'versions': collected}
        return versions


def version_descriptor(base_url, version, released_on):
    """Version Descriptor"""
    url = version_url(base_url, version)
    return {
        'id': version,
        'links': [
            {'href': url, 'rel': 'self', },
            {'href': 'https://wiki.onap.org/pages'
                     '/viewpage.action?pageId=16005528',
             'rel': 'describedby', 'type': 'text/html', }],
        'media-types': [
            {'base': 'application/json', 'type': MEDIA_TYPE_JSON % version, }],
        'status': 'EXPERIMENTAL',
        'updated': released_on,
    }


def version_url(base_url, version_number):
    """Version URL"""
    return '%s/%s' % (base_url, version_number)
