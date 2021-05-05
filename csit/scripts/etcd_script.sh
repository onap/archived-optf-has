#!/bin/bash

#
# -------------------------------------------------------------------------
#   Copyright (C) 2021 Wipro Limited.
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

echo "### This is ${WORKSPACE}/scripts/etcd_script.sh"

NODE=0.0.0.0

REGISTRY=gcr.io/etcd-development/etcd

VERSION=v3.4.15

docker run -d \
  -p 2379:2379 \
  -p 2380:2380 \
  --name etcd ${REGISTRY}:${VERSION} \
  /usr/local/bin/etcd \
  --data-dir=/etcd-data --name node1 \
  --initial-advertise-peer-urls http://${NODE}:2380 --listen-peer-urls http://0.0.0.0:2380 \
  --advertise-client-urls http://${NODE}:2379 --listen-client-urls http://0.0.0.0:2379 \
  --initial-cluster node1=http://${NODE}:2380

sleep 10

docker exec etcd /usr/local/bin/etcdctl user add root --new-user-password root
docker exec etcd /usr/local/bin/etcdctl user add conductor --new-user-password conductor
docker exec etcd /usr/local/bin/etcdctl role add conductor
docker exec etcd /usr/local/bin/etcdctl user grant-role conductor root
docker exec etcd /usr/local/bin/etcdctl auth enable
