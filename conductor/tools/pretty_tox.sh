#!/usr/bin/env bash
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


set -o pipefail

TESTRARGS=$1

# --until-failure is not compatible with --subunit see:
#
# https://bugs.launchpad.net/testrepository/+bug/1411804
#
# this work around exists until that is addressed
if [[ "$TESTARGS" =~ "until-failure" ]]; then
    python setup.py testr --slowest --testr-args="$TESTRARGS" | subunit2junitxml --output-to=xunit-results.xml
else
    python setup.py testr --slowest --testr-args="--subunit $TESTRARGS" | subunit-1to2 | subunit2junitxml --no-passthrough --forward --output-to=xunit-results.xml | subunit-trace -f
fi
