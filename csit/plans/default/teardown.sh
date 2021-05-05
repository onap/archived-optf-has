#!/bin/bash
#
# Copyright 2016-2017 Huawei Technologies Co., Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


#
# add here below the killing of all docker containers used for optf/has CSIT testing
#
# Move logs to has

mkdir ${WORKSPACE}/archives/logs
docker logs cond-cont > ${WORKSPACE}/archives/logs/cond-cont.log
docker logs cond-api > ${WORKSPACE}/archives/logs/cond-api.log
docker logs cond-data > ${WORKSPACE}/archives/logs/cond-data.log
docker logs cond-solv > ${WORKSPACE}/archives/logs/cond-solv.log
docker logs cond-resv > ${WORKSPACE}/archives/logs/cond-resv.log


#
# optf/has scripts docker containers killing";
#
echo "# optf/has has scripts calling";
source ${WORKSPACE}/scripts/has_teardown_script.sh

echo "# optf/has simulator scripts calling";
source ${WORKSPACE}/scripts/simulator_teardown_script.sh

echo "# optf/has etcd scripts calling";
source ${WORKSPACE}/scripts/etcd_teardown_script.sh

echo "# aaf-sms teardown.sh script";
#kill-instance.sh sms
#kill-instance.sh vault
docker stop sms
docker stop vault

docker rm sms
docker rm vault

docker volume prune -f

rm -rf ${WORKSPACE}/plans/default/config
