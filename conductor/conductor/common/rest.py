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

"""REST Helper"""

import json
from os import path

from oslo_config import cfg
from oslo_log import log
import requests
from requests.auth import HTTPBasicAuth
from six.moves.urllib import parse

from conductor.i18n import _LE, _LW  # pylint: disable=W0212

LOG = log.getLogger(__name__)

CONF = cfg.CONF


class RESTException(IOError):
    """Basic exception for errors raised by REST"""


class CertificateFileNotFoundException(RESTException, ValueError):
    """Certificate file was not found"""


class MissingURLNetlocException(RESTException, ValueError):
    """URL is missing a host/port"""


class ProhibitedURLSchemeException(RESTException, ValueError):
    """URL is using a prohibited scheme"""


class REST(object):
    """Helper class for REST operations."""

    server_url = None
    timeout = None

    # Why the funny looking connect/read timeouts? Here, read this:
    # http://docs.python-requests.org/en/master/user/advanced/#timeouts

    def __init__(self, server_url, retries=3, connect_timeout=3.05,
                 read_timeout=12.05, username=None, password=None,
                 cert_file=None, cert_key_file=None, ca_bundle_file=None,
                 log_debug=False):
        """Initializer."""
        parsed = parse.urlparse(server_url, 'http')
        if parsed.scheme not in ('http', 'https'):
            raise ProhibitedURLSchemeException
        if not parsed.netloc:
            raise MissingURLNetlocException

        for file_path in (cert_file, cert_key_file, ca_bundle_file):
            if file_path and not path.exists(file_path):
                raise CertificateFileNotFoundException

        self.server_url = server_url.rstrip('/')
        self.retries = int(retries)
        self.timeout = (float(connect_timeout), float(read_timeout))
        self.log_debug = log_debug
        self.username = username
        self.password = password
        self.cert = cert_file
        self.key = cert_key_file
        self.verify = ca_bundle_file

        # FIXME(jdandrea): Require a CA bundle; do not suppress warnings.
        # This is here due to an A&AI's cert/server name mismatch.
        # Permitting this defeats the purpose of using SSL/TLS.
        if self.verify == "":
            requests.packages.urllib3.disable_warnings()
            self.verify = False

        # Use connection pooling, kthx.
        # http://docs.python-requests.org/en/master/user/advanced/
        self.session = requests.Session()

    def request(self, method='get', content_type='application/json',
                path='', headers=None, data=None):
        """Performs HTTP request. Returns a requests.Response object."""
        if method not in ('post', 'get', 'put', 'delete'):
            method = 'get'
        method_fn = getattr(self.session, method)

        full_headers = {
            'Accept': content_type,
            'Content-Type': content_type,
        }
        if headers:
            full_headers.update(headers)
        full_url = '{}/{}'.format(self.server_url, path.lstrip('/').rstrip('/'))

        # Prepare the request args
        try:
            data_str = json.dumps(data) if data else None
        except (TypeError, ValueError):
            data_str = data
        kwargs = {
            'data': data_str,
            'headers': full_headers,
            'timeout': self.timeout,
            'cert': (self.cert, self.key),
            'verify': self.verify,
            'stream': False,
        }
        if self.username or self.password:
            LOG.debug("Using HTTPBasicAuth")
            kwargs['auth'] = HTTPBasicAuth(self.username, self.password)
        if self.cert and self.key:
            LOG.debug("Using SSL/TLS Certificate/Key")

        if self.log_debug:
            LOG.debug("Request: {} {}".format(method.upper(), full_url))
            if data:
                LOG.debug("Request Body: {}".format(json.dumps(data)))
        response = None
        for attempt in range(self.retries):
            if attempt > 0:
                # No need to show 400 bad requests from Music - Ignorable when lock cannot be received at one particular point in time
                if "MUSIC" not in full_url:
                    LOG.warn(_LW("Retry #{}/{}").format(
                    attempt + 1, self.retries))

            try:
                response = method_fn(full_url, **kwargs)

                # We shouldn't have to do this since stream is set to False,
                # but we're gonna anyway. See "Body Content Workflow" here:
                # http://docs.python-requests.org/en/master/user/advanced/
                response.close()

                if not response.ok:
                    # No need to show 400 bad requests from Music - Ignorable when lock cannot be received at one particular point in time
                    if "MUSIC" not in full_url:
                        LOG.warn("Response Status: {} {}".format(
                            response.status_code, response.reason))
                if self.log_debug and response.text:
                    try:
                        response_dict = json.loads(response.text)
                        LOG.debug("Response JSON: {}".format(
                            json.dumps(response_dict)))
                    except ValueError:
                        LOG.debug("Response Body: {}".format(response.text))
                #response._content = response._content.decode()
                if response.ok:
                    break
            except requests.exceptions.RequestException as err:
                LOG.error("Exception: %s", err.args)

        # Response.__bool__ returns false if status is not ok. Ruh roh!
        # That means we must check the object type vs treating it as a bool.
        # More info: https://github.com/kennethreitz/requests/issues/2002
        if isinstance(response, requests.models.Response) and not response.ok:
            # No need to show 400 bad requests from Music - Ignorable when lock cannot be received at one particular point in time
            if "MUSIC" not in full_url:
                LOG.error(_LE("Status {} {} after {} retries for URL: {}").format(
                    response.status_code, response.reason, self.retries, full_url))
        return response
