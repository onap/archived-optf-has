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

import sys
from conductor.common.utils import cipherUtils


def main():

    if len(sys.argv) != 4:
        print("Invalid input - usage --> (options(encrypt/decrypt) input-value with-key)")
        return

    enc_dec = sys.argv[1]
    valid_option_values = ['encrypt', 'decrypt']
    if enc_dec not in valid_option_values:
        print("Invalid input - usage --> (options(encrypt/decrypt) input-value with-key)")
        print("Option value can only be one of {}".format(valid_option_values))
        print("You entered '{}'".format(enc_dec))
        return

    input_string = sys.argv[2]
    with_key = sys.argv[3]

    print("You've requested '{}' to be '{}ed' using key '{}'".format(input_string, enc_dec, with_key))
    print("You can always perform the reverse operation (encrypt/decrypt) using the same key"
          "to be certain you get the same results back'")

    util = cipherUtils.AESCipher.get_instance(with_key)
    #util = CipherUtil.AESCipher(with_key)

    if enc_dec.lower() == 'encrypt':
        result = util.encrypt(input_string)
    else:
        result = util.decrypt(input_string)

    print("Your result: {}".format(result))

