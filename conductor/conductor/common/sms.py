#
# -------------------------------------------------------------------------
#   Copyright (c) 2018 Intel Corporation Intellectual Property
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

'''Secret Management Service Integration'''
from conductor.common import config_loader
from onapsmsclient import Client

from oslo_config import cfg
from oslo_log import log
import conductor.data.plugins.inventory_provider.aai
import conductor.api.controllers.v1.plans
import conductor.common.music.api
import conductor.data.plugins.service_controller.sdnc
from conductor.common.utils import cipherUtils

LOG = log.getLogger(__name__)

CONF = cfg.CONF

AAF_SMS_OPTS = [
    cfg.BoolOpt('is_enabled',
               default=True,
               help='Is Secret Management service enabled'),
    cfg.StrOpt('aaf_sms_url',
               default='https://aaf-sms.onap:10443',
               help='Base URL for SMS, up to and not including '
                    'the version, and without a trailing slash.'),
    cfg.IntOpt('aaf_sms_timeout',
               default=30,
               help='Timeout for SMS API Call'),
    cfg.StrOpt('aaf_ca_certs',
               default='AAF_RootCA.cer',
               help='Path to the cacert that will be used to verify '
                    'If this is None, verify will be False and the server cert'
                    'is not verified by the client.'),
    cfg.StrOpt('secret_domain',
               default='has',
               help='Domain Name for HAS')
]

CONF.register_opts(AAF_SMS_OPTS, group='aaf_sms')
config_spec = {
    "preload_secrets": "../preload_secrets.yaml"
}


def preload_secrets():
    """ This is intended to load the secrets required for testing Application
        Actual deployment will have a preload script. Make sure the config is
        in sync"""
    preload_config = config_loader.load_config_file(
        config_spec.get("preload_secrets"))
    domain = preload_config.get("domain")
    config = CONF.aaf_sms
    sms_url = config.aaf_sms_url
    timeout = config.aaf_sms_timeout
    cacert = config.aaf_ca_certs
    sms_client = Client(url=sms_url, timeout=timeout, cacert=cacert)
    domain_uuid = sms_client.createDomain(domain)
    LOG.debug("Created domain {} with uuid {}".format(domain, domain_uuid))
    secrets = preload_config.get("secrets")
    for secret in secrets:
        sms_client.storeSecret(domain, secret.get('name'),
                               secret.get('values'))
    LOG.debug("Preload secrets complete")


def retrieve_secrets():
    """Get all secrets under the domain name"""
    secret_dict = dict()
    config = CONF.aaf_sms
    sms_url = config.aaf_sms_url
    timeout = config.aaf_sms_timeout
    cacert = config.aaf_ca_certs
    domain = config.secret_domain
    sms_client = Client(url=sms_url, timeout=timeout, cacert=cacert)
    secrets = sms_client.getSecretNames(domain)
    for secret in secrets:
        values = sms_client.getSecret(domain, secret)
        secret_dict[secret] = values
    LOG.debug("Secret Dictionary Retrieval Success")
    return secret_dict


def load_secrets():
    config = CONF
    secret_dict = retrieve_secrets()
    config.set_override('username', secret_dict['aai']['username'], 'aai')
    config.set_override('password', decrypt_pass(secret_dict['aai']['password']), 'aai')
    config.set_override('username', secret_dict['conductor_api']['username'], 'conductor_api')
    config.set_override('password', decrypt_pass(secret_dict['conductor_api']['password']), 'conductor_api')
    config.set_override('aafuser', secret_dict['music_api']['aafuser'], 'music_api')
    config.set_override('aafpass', decrypt_pass(secret_dict['music_api']['aafpass']), 'music_api')
    config.set_override('aafns', secret_dict['music_api']['aafns'], 'music_api')
    config.set_override('username', secret_dict['sdnc']['username'], 'sdnc')
    config.set_override('password', decrypt_pass(secret_dict['sdnc']['password']), 'sdnc')
    config.set_override('username', secret_dict['aaf_api']['username'], 'aaf_api')
    config.set_override('password', decrypt_pass(secret_dict['aaf_api']['password']), 'aaf_api')
    config.set_override('aaf_conductor_user', secret_dict['aaf_api']['aaf_conductor_user'], 'aaf_api')
    config.set_override('username', secret_dict['sdc']['username'], 'sdc')
    config.set_override('password', decrypt_pass(secret_dict['sdc']['password']), 'sdc')


def decrypt_pass(passwd):
    if not CONF.auth.appkey or passwd == '' or passwd == 'NA':
        return passwd
    else:
        return cipherUtils.AESCipher.get_instance().decrypt(passwd)


def delete_secrets():
    """ This is intended to delete the secrets for a clean initialization for
        testing Application. Actual deployment will have a preload script.
        Make sure the config is in sync"""
    config = CONF.aaf_sms
    sms_url = config.aaf_sms_url
    timeout = config.aaf_sms_timeout
    cacert = config.aaf_ca_certs
    domain = config.secret_domain
    sms_client = Client(url=sms_url, timeout=timeout, cacert=cacert)
    ret_val = sms_client.deleteDomain(domain)
    LOG.debug("Clean up complete")
    return ret_val


if __name__ == "__main__":
    # Initialize Secrets from SMS
    preload_secrets()

    # Retrieve Secrets from SMS and load to secret cache
    # Use the secret_cache instead of config files
    secret_cache = retrieve_secrets()

    # Clean up Delete secrets and domain
    delete_secrets()
