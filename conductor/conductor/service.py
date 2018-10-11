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

import sys

# from keystoneauth1 import loading as ka_loading
from conductor.common import sms
from oslo_config import cfg
import oslo_i18n
from oslo_log import log
# from oslo_policy import opts as policy_opts
from oslo_reports import guru_meditation_report as gmr

from conductor.conf import defaults
# from conductor import keystone_client
from conductor import messaging
from conductor import version

OPTS = [
    # cfg.StrOpt('host',
    #            default=socket.gethostname(),
    #            sample_default='<your_hostname>',
    #            help='Name of this node, which must be valid in an AMQP '
    #            'key. Can be an opaque identifier. For ZeroMQ only, must '
    #            'be a valid host name, FQDN, or IP address.'),
    # cfg.IntOpt('http_timeout',
    #            default=600,
    #            help='Timeout seconds for HTTP requests. Set it to None to '
    #                 'disable timeout.'),
    cfg.StrOpt('keyspace',
               default='conductor',
               help='Music keyspace for content'),
    cfg.IntOpt('delay_time',
                default=2,
                help='Delay time (Seconds) for MUSIC requests. Set it to 2 seconds '
                     'by default.'),
    #TODO(larry): move to a new section [feature_supported] in config file
    cfg.BoolOpt('HPA_enabled',
                default=True)
]
cfg.CONF.register_opts(OPTS)

# DATA_OPT = cfg.IntOpt('workers',
#                       default=1,
#                       min=1,
#                       help='Number of workers for data service, '
#                            'default value is 1.')
# cfg.CONF.register_opt(DATA_OPT, 'data')
#
# PARSER_OPT = cfg.IntOpt('workers',
#                         default=1,
#                         min=1,
#                         help='Number of workers for parser service. '
#                              'default value is 1.')
# cfg.CONF.register_opt(PARSER_OPT, 'parser')
#
# SOLVER_OPT = cfg.IntOpt('workers',
#                         default=1,
#                         min=1,
#                         help='Number of workers for solver service. '
#                              'default value is 1.')
# cfg.CONF.register_opt(SOLVER_OPT, 'solver')

# keystone_client.register_keystoneauth_opts(cfg.CONF)


def prepare_service(argv=None, config_files=None):
    if argv is None:
        argv = sys.argv

    # FIXME(sileht): Use ConfigOpts() instead
    conf = cfg.CONF

    oslo_i18n.enable_lazy()
    log.register_options(conf)
    log_levels = (conf.default_log_levels +
                  ['futurist=INFO'])
    log.set_defaults(default_log_levels=log_levels)
    defaults.set_cors_middleware_defaults()
    # policy_opts.set_defaults(conf)

    conf(argv[1:], project='conductor', validate_default_values=True,
         version=version.version_info.version_string(),
         default_config_files=config_files)

    # ka_loading.load_auth_from_conf_options(conf, "service_credentials")

    log.setup(conf, 'conductor')
    # NOTE(liusheng): guru cannot run with service under apache daemon, so when
    # conductor-api running with mod_wsgi, the argv is [], we don't start
    # guru.
    if argv:
        gmr.TextGuruMeditation.setup_autorun(version)
    messaging.setup()
    # TODO(Dileep): Uncomment once Helm charts to preload secrets available
    # sms.load_secrets()
    return conf
