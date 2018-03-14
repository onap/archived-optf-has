#!/bin/bash
BUILD_ARGS="--no-cache"
ORG="onap"
VERSION="1.1.1"
STAGING="1.1.1-STAGING"
PROJECT="optf-has"
DOCKER_REPOSITORY="nexus3.onap.org:10003"
IMAGE_NAME="${DOCKER_REPOSITORY}/${ORG}/${PROJECT}"
TIMESTAMP=$(date +"%Y%m%dT%H%M%S")
 
if [ $HTTP_PROXY ]; then
BUILD_ARGS+=" --build-arg HTTP_PROXY=${HTTP_PROXY}"
fi
if [ $HTTPS_PROXY ]; then
    BUILD_ARGS+=" --build-arg HTTPS_PROXY=${HTTPS_PROXY}"
fi
 
function build_image(){
     echo Building Image 
     docker build -t ${IMAGE_NAME}:${VERSION} -t ${IMAGE_NAME}:latest -t ${IMAGE_NAME}:${STAGING}  conductor/docker
     echo ... Built
}

function push_image(){
     echo Pushing image starts.
     build_image 	     

     docker push ${IMAGE_NAME}:${VERSION}
     docker push ${IMAGE_NAME}:latest
     docker push ${IMAGE_NAME}:STAGING

     echo ... Pushed $1
}

push_image 
 
