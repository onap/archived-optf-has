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
echo "### This is ${WORKSPACE}/scripts/has_script.sh"
#
# add here whatever commands is needed to prepare the optf/has CSIT testing
#

# assume the base is /tmp dir
DIR=/tmp

# the directory of the script
echo ${DIR}
cd ${DIR}

# create directory for volume and copy configuration file
# run docker containers
COND_CONF=/tmp/conductor/properties/conductor.conf
LOG_CONF=/tmp/conductor/properties/log.conf
IMAGE_NAME=nexus3.onap.org:10003/onap/optf-has
IMAGE_VER=latest
BUNDLE=/tmp/conductor/properties/AAF_RootCA.cer

mkdir -p /tmp/conductor/properties
mkdir -p /tmp/sms/properties
mkdir -p /tmp/conductor/logs
cp ${WORKSPACE}/scripts/has-properties/conductor.conf.onap /tmp/conductor/properties/conductor.conf
cp ${WORKSPACE}/scripts/has-properties/log.conf.onap /tmp/conductor/properties/log.conf
cp ${WORKSPACE}/scripts/has-properties/AAF_RootCA.cer /tmp/conductor/properties/AAF_RootCA.cer
cp ${WORKSPACE}/scripts/has-properties/has.json /tmp/sms/properties/has.json
#chmod -R 777 /tmp/conductor/properties

ETCD_IP=`docker inspect --format '{{ .NetworkSettings.Networks.bridge.IPAddress}}' etcd`
echo "ETCD_IP=${ETCD_IP}"

SMS_IP=`${WORKSPACE}/scripts/get-instance-ip.sh sms`
echo "SMS_IP=${SMS_IP}"

# change ETCD reference to the local instance
sed  -i -e "s%etcd_ip%${ETCD_IP}%g" /tmp/conductor/properties/conductor.conf

AAISIM_IP=`docker inspect --format '{{ .NetworkSettings.Networks.bridge.IPAddress}}' aaisim`
echo "AAISIM_IP=${AAISIM_IP}"

# change AAI reference to the local instance
sed  -i -e "s%localhost:8081/%${AAISIM_IP}:8081/%g" /tmp/conductor/properties/conductor.conf

SDCSIM_IP=`docker inspect --format '{{ .NetworkSettings.Networks.bridge.IPAddress}}' sdcsim`
echo "SDCSIM_IP=${SDCSIM_IP}"

# change SDC reference to the local instance
sed  -i -e "s%localhost:9595/%${SDCSIM_IP}:9595/%g" /tmp/conductor/properties/conductor.conf


MULTICLOUDSIM_IP=`docker inspect --format '{{ .NetworkSettings.Networks.bridge.IPAddress}}' multicloudsim`
echo "MULTICLOUDSIM_IP=${MULTICLOUDSIM_IP}"

# change MULTICLOUD reference to the local instance
sed  -i -e "s%msb.onap.org:8082/%${MULTICLOUDSIM_IP}:8082/%g" /tmp/conductor/properties/conductor.conf

AAFSIM_IP=`docker inspect --format '{{ .NetworkSettings.Networks.bridge.IPAddress}}' aafsim`
echo "AAFSIM_IP=${AAFSIM_IP}"

# change AAF reference to the local instance
sed  -i -e "s%localhost:8100/%${AAFSIM_IP}:8100/%g" /tmp/conductor/properties/conductor.conf

#SMS
sed  -i -e "s%aaf-sms.onap:10443%${SMS_IP}:10443%g" /tmp/conductor/properties/conductor.conf
#Preload secrets
docker exec --user root -i sms /bin/sh -c "mkdir -p /preload/config"
docker cp /tmp/sms/properties/has.json sms:/preload/config/has.json
docker exec --user root -i sms /bin/sh -c "/sms/bin/preload -cacert /sms/certs/aaf_root_ca.cer -jsondir /preload/config -serviceport 10443 -serviceurl http://localhost"
docker logs vault

#onboard conductor into music
# echo "Query MUSIC to check for reachability. Query Version"
# curl -vvvvv --noproxy "*" --request GET http://${MUSIC_IP}:8080/MUSIC/rest/v2/version -H "Content-Type: application/json"

# echo "Onboard conductor into music"
# curl -vvvvv --noproxy "*" --request POST http://${MUSIC_IP}:8080/MUSIC/rest/v2/admin/onboardAppWithMusic -H "Content-Type: application/json" -H "Authorization: Basic Y29uZHVjdG9yOmMwbmR1Y3Qwcg==" --data @${WORKSPACE}/tests/has/data/onboard.json

docker run -d --name cond-cont --user root -v ${COND_CONF}:/usr/local/bin/conductor.conf -v ${LOG_CONF}:/usr/local/bin/log.conf -v ${BUNDLE}:/usr/local/bin/AAF_RootCA.cer ${IMAGE_NAME}:${IMAGE_VER} python /usr/local/bin/conductor-controller --config-file=/usr/local/bin/conductor.conf
sleep 15
docker run -d --name cond-api --user root -p "8091:8091" -v ${COND_CONF}:/usr/local/bin/conductor.conf -v ${LOG_CONF}:/usr/local/bin/log.conf -v ${BUNDLE}:/usr/local/bin/AAF_RootCA.cer ${IMAGE_NAME}:${IMAGE_VER} python /usr/local/bin/conductor-api --port=8091 -- --config-file=/usr/local/bin/conductor.conf
sleep 15
docker run -d --name cond-solv --user root -v ${COND_CONF}:/usr/local/bin/conductor.conf -v ${LOG_CONF}:/usr/local/bin/log.conf -v ${BUNDLE}:/usr/local/bin/AAF_RootCA.cer ${IMAGE_NAME}:${IMAGE_VER} python /usr/local/bin/conductor-solver --config-file=/usr/local/bin/conductor.conf
sleep 15
docker run -d --name cond-resv --user root -v ${COND_CONF}:/usr/local/bin/conductor.conf -v ${LOG_CONF}:/usr/local/bin/log.conf -v ${BUNDLE}:/usr/local/bin/AAF_RootCA.cer ${IMAGE_NAME}:${IMAGE_VER} python /usr/local/bin/conductor-reservation --config-file=/usr/local/bin/conductor.conf
sleep 5
docker run -d --name cond-data --user root -v ${COND_CONF}:/usr/local/bin/conductor.conf -v ${LOG_CONF}:/usr/local/bin/log.conf -v ${BUNDLE}:/usr/local/bin/AAF_RootCA.cer ${IMAGE_NAME}:${IMAGE_VER} python /usr/local/bin/conductor-data --config-file=/usr/local/bin/conductor.conf
sleep 15

COND_IP=`docker inspect --format '{{ .NetworkSettings.Networks.bridge.IPAddress}}' cond-api`
${WORKSPACE}/scripts/wait_for_port.sh ${COND_IP} 8091

echo "inspect docker things for tracing purpose"
docker inspect cond-data
docker inspect cond-cont
docker inspect cond-api
docker inspect cond-solv
docker inspect cond-resv

# echo "dump music content just after conductor is started"
# docker exec music-db /usr/bin/nodetool status
# docker exec music-db /usr/bin/cqlsh -unelson24 -pwinman123 -e 'SELECT * FROM system_schema.keyspaces'
# docker exec music-db /usr/bin/cqlsh -unelson24 -pwinman123 -e 'SELECT * FROM admin.keyspace_master'
