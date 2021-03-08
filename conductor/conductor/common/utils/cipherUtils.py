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

import base64
from Cryptodome.Cipher import AES
from Cryptodome import Random
import hashlib
from oslo_config import cfg

CONF = cfg.CONF

cipher_opts = [
    cfg.StrOpt('appkey',
               default='ch00se@g003ntropy',
               help='Master key to secure other secrets')
]

CONF.register_opts(cipher_opts, group='auth')


class AESCipher(object):
    __instance = None

    @staticmethod
    def get_instance(key=None):
        if AESCipher.__instance is None:
            print('Creating the singleton instance')
            AESCipher(key)
        return AESCipher.__instance

    def __init__(self, key=None):
        if AESCipher.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            AESCipher.__instance = self

        self.bs = 32
        if key is None:
            key = CONF.auth.appkey  # ---> python3.8 Code version code
            # key= CONF.auth.appkey.encode() ---> Python 2.7 version code
        # in Python 3+ key is already a b'' type so no need to encode it again.

        self.key = hashlib.sha256(key.encode()).digest()

    def encrypt(self, raw):
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw))

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s) - 1:])]
