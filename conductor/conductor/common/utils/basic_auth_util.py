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

import base64

from conductor.i18n import _, _LI, _LE
from oslo_log import log

LOG = log.getLogger(__name__)


def encode(user_id, password):
    """ Provide the basic authencation encoded value in an 'Authorization' Header """

    user_pass = str(user_id) + ":" + str(password)
    base64_val = base64.b64encode(user_pass)
    authorization_val = _LE("Basic {}".format(base64_val))

    return authorization_val
