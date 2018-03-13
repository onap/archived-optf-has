#!/bin/bash
BUILD_ARGS="--no-cache"
ORG="onap"
VERSION="1.1.0"
PROJECT="optf"
IMAGE="api"
DOCKER_REPOSITORY="nexus3.onap.org:10003"
IMAGE_NAME="${DOCKER_REPOSITORY}/${ORG}/${PROJECT}/${IMAGE}"
TIMESTAMP=$(date +"%Y%m%dT%H%M%S")
 
if [ $HTTP_PROXY ]; then
BUILD_ARGS+=" --build-arg HTTP_PROXY=${HTTP_PROXY}"
fi
if [ $HTTPS_PROXY ]; then
    BUILD_ARGS+=" --build-arg HTTPS_PROXY=${HTTPS_PROXY}"
fi
 
function tag {
     echo "Tagging !!!"
     docker tag api "nexus3.onap.org:10003/onap/optf/api"
     docker tag data "nexus3.onap.org:10003/onap/optf/data"
     docker tag controller "nexus3.onap.org:10003/onap/optf/controller"
     docker tag solver "nexus3.onap.org:10003/onap/optf/solver"
     docker tag reservation "nexus3.onap.org:10003/onap/optf/reservation"
}

function push_image {
     echo "Start push ${IMAGE_NAME}:latest"
     
     tag
     docker push "nexus3.onap.org:10003/onap/optf/api"
     docker push "nexus3.onap.org:10003/onap/optf/data"
     docker push "nexus3.onap.org:10003/onap/optf/controller"
     docker push "nexus3.onap.org:10003/onap/optf/solver"
     docker push "nexus3.onap.org:10003/onap/optf/reservation"
     
     #docker push ${IMAGE_NAME}:latest
     #push_image_tag ${IMAGE_NAME}:${VERSION}-SNAPSHOT-latest
     #push_image_tag ${IMAGE_NAME}:${VERSION}-STAGING-latest
     #push_image_tag ${IMAGE_NAME}:${VERSION}-STAGING-${TIMESTAMP}
 }
push_image
