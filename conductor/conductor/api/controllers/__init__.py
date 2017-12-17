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

from os import path

from notario import exceptions
from notario.utils import forced_leaf_validator
import pecan
import six


#
# Error Handler
#
def error(url, msg=None, **kwargs):
    """Error handler"""
    if msg:
        pecan.request.context['error_message'] = msg
    if kwargs:
        pecan.request.context['kwargs'] = kwargs
    url = path.join(url, '?error_message=%s' % msg)
    pecan.redirect(url, internal=True)


#
# Notario Custom Validators
#
@forced_leaf_validator
def string_or_dict(_object, *args):
    """Validator - Must be Basestring or Dictionary"""
    error_msg = 'not of type dictionary or string'

    if isinstance(_object, six.string_types):
        return
    if isinstance(_object, dict):
        return
    raise exceptions.Invalid('dict or basestring type', pair='value',
                             msg=None, reason=error_msg, *args)
