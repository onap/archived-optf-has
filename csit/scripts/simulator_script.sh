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
echo "### This is ${WORKSPACE}/scripts/simulator_script.sh"
#
# add here whatever commands is needed to prepare the optf/has CSIT testing
#
if [ ${USER} != 'jenkins' ]; then

    # add proxy settings into this script when you work behind a proxy
    ${WORKSPACE}/scripts/has_proxy_settings.sh ${WORK_DIR}

fi

# prepare aaisim
cd ${WORKSPACE}/../conductor/conductor/tests/functional/simulators/

# run aaisim
./run_aaisim.sh

AAISIM_IP=`docker inspect --format '{{ .NetworkSettings.Networks.bridge.IPAddress}}' aaisim`
echo "AAISIM_IP=${AAISIM_IP}"

${WORKSPACE}/scripts/wait_for_port.sh ${AAISIM_IP} 8081

# prepare multicloudsim
cd ${WORKSPACE}/../conductor/conductor/tests/functional/simulators/multicloudsim/

# check Dockerfile content
cat ./Dockerfile

# build multicloudsim
docker build -t multicloudsim .

# run multicloudsim
docker run -d --name multicloudsim -p 8082:8082  multicloudsim

MULTICLOUDSIM_IP=`docker inspect --format '{{ .NetworkSettings.Networks.bridge.IPAddress}}' multicloudsim`
echo "MULTICLOUDSIM_IP=${MULTICLOUDSIM_IP}"

${WORKSPACE}/scripts/wait_for_port.sh ${MULTICLOUDSIM_IP} 8082


# prepare sdcsim
cd ${WORKSPACE}/../conductor/conductor/tests/functional/simulators/sdcsim/

# check Dockerfile content
cat ./Dockerfile

# build multicloudsim
docker build -t sdcsim .

# run multicloudsim
docker run -d --name sdcsim -p 9595:9595  sdcsim

SDCSIM_IP=`docker inspect --format '{{ .NetworkSettings.Networks.bridge.IPAddress}}' sdcsim`
echo "SDCSIM_IP=${SDCSIM_IP}"

${WORKSPACE}/scripts/wait_for_port.sh ${SDCSIM_IP} 9595


# prepare aafsim
echo "simulator_script: prepare aafsim "
cd ${WORKSPACE}/../conductor/conductor/tests/functional/simulators/aafsim/

# check Dockerfile content
echo "simulator_script: Dockerfile "
cat ./Dockerfile

# build aafsim
echo "simulator_script: build docker "
docker build -t aafsim .

# run aafsim
echo "simulator_script: run docker "
docker run -d --name aafsim -p 8100:8100 aafsim

AAFSIM_IP=`docker inspect --format '{{ .NetworkSettings.Networks.bridge.IPAddress}}' aafsim`
echo "simulator_script: AAFSIM_IP=${AAFSIM_IP}"

#echo "simulator_script: wait_for_port"
${WORKSPACE}/scripts/wait_for_port.sh ${AAFSIM_IP} 8100

# wait a while before continuing
sleep 2

echo "inspect docker things for tracing purpose"
docker inspect aaisim
docker inspect multicloudsim
docker inspect aafsim
