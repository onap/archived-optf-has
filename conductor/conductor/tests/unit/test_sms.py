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
import unittest
from uuid import uuid4

import requests_mock

import conductor.common.sms as SMS
from oslo_config import cfg


class TestSMS(unittest.TestCase):

    def setUp(self):
        self.config = cfg.CONF.aaf_sms
        self.base_domain_url = '{}/v1/sms/domain'
        self.domain_url = '{}/v1/sms/domain/{}'
        self.secret_url = self.domain_url + '/secret'

    @requests_mock.mock()
    def test_sms(self, mock_sms):
        ''' NOTE: preload_secret during the deployment using a preload script.
                  For test purposes we need to do preload ourselves'''
        sms_url = self.config.aaf_sms_url

        # JSON Data responses
        secretnames = {'secretnames': ['s1', 's2', 's3', 's4']}
        secretvalues = {'values': {'Password': '', 'UserName': ''}}
        expecect_secret_dict = dict()
        for secret in secretnames['secretnames']:
            expecect_secret_dict[secret] = secretvalues['values']

        # Part 1 : Preload Secrets ONLY FOR TEST
        # Mock requests for preload_secret
        cd_url = self.base_domain_url.format(sms_url)
        domain_uuid1 = str(uuid4())
        domain_name = self.config.secret_domain
        s_url = self.secret_url.format(sms_url, domain_name)
        mock_sms.post(cd_url, status_code=200, json={'uuid': domain_uuid1})
        mock_sms.post(s_url, status_code=200)
        # Initialize Secrets from SMS
        SMS.preload_secrets()

        # Part 2: Retrieve Secret Test
        # Mock requests for retrieve_secrets

        d_url = self.domain_url.format(sms_url, domain_name)
        s_url = self.secret_url.format(sms_url, domain_name)

        # Retrieve Secrets from SMS and load to secret cache
        # Use the secret_cache instead of config files
        mock_sms.get(s_url, status_code=200, json=secretnames)
        for secret in secretnames['secretnames']:
            mock_sms.get('{}/{}'.format(s_url, secret),
                         status_code=200, json=secretvalues)
        secret_cache = SMS.retrieve_secrets()
        self.assertDictEqual(expecect_secret_dict, secret_cache,
                             'Failed to retrieve secrets')

        # Part 3: Clean up Delete secrets and domain
        # Mock requests for delete_secrets
        mock_sms.delete(d_url, status_code=200)
        self.assertTrue(SMS.delete_secrets())


if __name__ == "__main__":
    unittest.main()
