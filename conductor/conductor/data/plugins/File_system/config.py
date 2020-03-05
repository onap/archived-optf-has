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

import time

from oslo_config import cfg
from oslo_log import log

from conductor.common import rest
from conductor.common.utils import cipherUtils
from conductor.data.plugins.File_system import base
from conductor.i18n import _LE

LOG = log.getLogger(__name__)

CONF = cfg.CONF

CONFIG_OPTS = [
    cfg.IntOpt('cache_refresh_interval',
               default=1440,
               help='Interval with which to refresh the local cache, '
                    'in minutes.'),
]

CONF.register_opts(CONFIG_OPTS, group='config')


class CONFIG(base.FileSystemControllerBase):
    """SDN Service Controller"""

    def __init__(self):
        """Initializer"""

        # FIXME(jdandrea): Pass this in to init.
        self.conf = CONF
        self.file_path = ""

    def initialize(self):
        """Perform any late initialization."""
        # self.filter_candidates([])
        pass

    def candidate_request(self):
        """Performs HTTP request."""
        print "hello";

        # kwargs = {
        #     "method": method,
        #     "path": path,
        #     "data": data,
        # }
        #
        # # TODO(jdandrea): Move timing/response logging into the rest helper?
        # start_time = time.time()
        # response = self.rest.request(**kwargs)
        # elapsed = time.time() - start_time
        # LOG.debug("Total time for SDN-C request "
        #           "({0:}: {1:}): {2:.3f} sec".format(context, value, elapsed))
        #
        # if response is None:
        #     LOG.error(_LE("No response from SDN-C ({}: {})").
        #               format(context, value))
        #     raise Exception('SDN-C query {} timed out'.format(path))
        # elif response.status_code != 200:
        #     LOG.error(_LE("SDN-C request ({}: {}) returned HTTP "
        #                   "status {} {}, link: {}{}").
        #               format(context, value,
        #                      response.status_code, response.reason,
        #                      self.base, path))
        # return response

     def name(self):
        """Return human-readable name."""
        return "File_system"
