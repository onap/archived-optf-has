#!/bin/bash
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

run_tox_test()
{ 
  set -x
  CURDIR=$(pwd)
  TOXINIS=$(find . -name "tox.ini")
  for TOXINI in "${TOXINIS[@]}"; do
    DIR=$(echo "$TOXINI" | rev | cut -f2- -d'/' | rev)
    cd "${CURDIR}/${DIR}"
    rm -rf ./venv-tox ./.tox
    virtualenv ./venv-tox
    source ./venv-tox/bin/activate
    pip install --no-cache-dir --upgrade pip
    pip install --no-cache-dir --upgrade tox argparse
    pip freeze
    tox -e cover
    deactivate
    rm -rf ./venv-tox ./.tox
  done
}

run_tox_test
