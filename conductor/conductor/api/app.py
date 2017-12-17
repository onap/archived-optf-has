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

import os
import uuid

from oslo_config import cfg
from oslo_log import log
from paste import deploy
import pecan

from conductor.api import hooks
from conductor.api import middleware
from conductor import service

LOG = log.getLogger(__name__)

CONF = cfg.CONF

OPTS = [
    cfg.StrOpt('api_paste_config',
               default="api_paste.ini",
               help="Configuration file for WSGI definition of API."
               ),
]

API_OPTS = [
    cfg.BoolOpt('pecan_debug',
                default=False,
                help='Toggle Pecan Debug Middleware.'),
    cfg.IntOpt('default_api_return_limit',
               min=1,
               default=100,
               help='Default maximum number of items returned by API request.'
               ),
]

CONF.register_opts(OPTS)
CONF.register_opts(API_OPTS, group='api')

# Pull in service opts. We use them here.
OPTS = service.OPTS
CONF.register_opts(OPTS)

# Can call like so to force a particular config:
# conductor-api --port=8091 -- --config-file=my_config
#
# For api command-line options:
# conductor-api -- --help


def setup_app(pecan_config=None, conf=None):
    if conf is None:
        raise RuntimeError("No configuration passed")

    app_hooks = [
        hooks.ConfigHook(conf),
        hooks.MessagingHook(conf),
    ]

    pecan_config = pecan_config or {
        "app": {
            'root': 'conductor.api.controllers.root.RootController',
            'modules': ['conductor.api'],
        }
    }

    pecan.configuration.set_config(dict(pecan_config), overwrite=True)

    app = pecan.make_app(
        pecan_config['app']['root'],
        debug=conf.api.pecan_debug,
        hooks=app_hooks,
        wrap_app=middleware.ParsableErrorMiddleware,
        guess_content_type_from_ext=False,
        default_renderer='json',
        force_canonical=False,
    )

    return app


# pastedeploy uses ConfigParser to handle global_conf, since Python 3's
# ConfigParser doesn't allow storing objects as config values. Only strings
# are permitted. Thus, to be able to pass an object created before paste
# loads the app, we store them in a global variable. Then each loaded app
# stores it's configuration using a unique key to be concurrency safe.
global APPCONFIGS
APPCONFIGS = {}


def load_app(conf):
    global APPCONFIGS

    # Build the WSGI app
    cfg_file = None
    cfg_path = conf.api_paste_config
    if not os.path.isabs(cfg_path):
        cfg_file = conf.find_file(cfg_path)
    elif os.path.exists(cfg_path):
        cfg_file = cfg_path

    if not cfg_file:
        raise cfg.ConfigFilesNotFoundError([conf.api_paste_config])

    configkey = str(uuid.uuid4())
    APPCONFIGS[configkey] = conf

    LOG.info("Full WSGI config used: %s" % cfg_file)
    return deploy.loadapp("config:" + cfg_file,
                          global_conf={'configkey': configkey})


def app_factory(global_config, **local_conf):
    global APPCONFIGS
    conf = APPCONFIGS.get(global_config.get('configkey'))
    return setup_app(conf=conf)


def build_wsgi_app(argv=None):
    return load_app(service.prepare_service(argv=argv))
