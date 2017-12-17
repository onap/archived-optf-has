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

import traceback

from oslo_log import log
import pecan
from webob.exc import status_map

from conductor.i18n import _

LOG = log.getLogger(__name__)


def error_wrapper(func):
    """Error decorator."""
    def func_wrapper(self, **kw):
        """Wrapper."""

        kwargs = func(self, **kw)
        status = status_map.get(pecan.response.status_code)
        message = getattr(status, 'explanation', '')
        explanation = \
            pecan.request.context.get('error_message', message)
        error_type = status.__name__
        title = status.title
        traceback = getattr(kwargs, 'traceback', None)

        LOG.error(explanation)

        # Modeled after Heat's format
        error = {
            "explanation": explanation,
            "code": pecan.response.status_code,
            "error": {
                "message": message,
                "type": error_type,
            },
            "title": title,
        }
        if traceback:
            error['error']['traceback'] = traceback
        return error
    return func_wrapper


class ErrorsController(object):
    """Errors Controller /errors/{error_name}"""

    @pecan.expose('json')
    @error_wrapper
    def schema(self, **kw):
        """400"""
        pecan.request.context['error_message'] = \
            str(pecan.request.validation_error)
        pecan.response.status = 400
        return pecan.request.context.get('kwargs')

    @pecan.expose('json')
    @error_wrapper
    def invalid(self, **kw):
        """400"""
        pecan.response.status = 400
        return pecan.request.context.get('kwargs')

    @pecan.expose()
    def unauthorized(self, **kw):
        """401"""
        # This error is terse and opaque on purpose.
        # Don't give any clues to help AuthN along.
        pecan.response.status = 401
        pecan.response.content_type = 'text/plain'
        LOG.error('unauthorized')
        traceback.print_stack()
        LOG.error(self.__class__)
        LOG.error(kw)
        pecan.response.body = _('Authentication required')
        LOG.error(pecan.response.body)
        return pecan.response

    @pecan.expose('json')
    @error_wrapper
    def forbidden(self, **kw):
        """403"""
        pecan.response.status = 403
        return pecan.request.context.get('kwargs')

    @pecan.expose('json')
    @error_wrapper
    def not_found(self, **kw):
        """404"""
        pecan.response.status = 404
        return pecan.request.context.get('kwargs')

    @pecan.expose('json')
    @error_wrapper
    def not_allowed(self, **kw):
        """405"""
        kwargs = pecan.request.context.get('kwargs')
        if kwargs:
            allow = kwargs.get('allow', None)
            if allow:
                pecan.response.headers['Allow'] = allow
        pecan.response.status = 405
        return kwargs

    @pecan.expose('json')
    @error_wrapper
    def conflict(self, **kw):
        """409"""
        pecan.response.status = 409
        return pecan.request.context.get('kwargs')

    @pecan.expose('json')
    @error_wrapper
    def server_error(self, **kw):
        """500"""
        pecan.response.status = 500
        return pecan.request.context.get('kwargs')

    @pecan.expose('json')
    @error_wrapper
    def unimplemented(self, **kw):
        """501"""
        pecan.response.status = 501
        return pecan.request.context.get('kwargs')

    @pecan.expose('json')
    @error_wrapper
    def unavailable(self, **kw):
        """503"""
        pecan.response.status = 503
        return pecan.request.context.get('kwargs')
