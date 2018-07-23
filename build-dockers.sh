#!/bin/bash

# The script starts in the root folder of the repo, which has the following outline
# We fetch the version information from version.properties, build docker files and
# do a docker push. Since the job will be run under Jenkins, it will have the Nexus
# credentials

set -e

BUILD_ARGS="--no-cache"
ORG="onap"
PROJECT="optf-has"
DOCKER_REPOSITORY="nexus3.onap.org:10003"
IMAGE_NAME="${DOCKER_REPOSITORY}/${ORG}/${PROJECT}"

# Version properties
source version.properties
VERSION=$release_version
SNAPSHOT=$snapshot_version
STAGING=${release_version}-STAGING
TIMESTAMP=$(date +"%Y%m%dT%H%M%S")Z

if [ $HTTP_PROXY ]; then
    BUILD_ARGS+=" --build-arg HTTP_PROXY=${HTTP_PROXY}"
fi
if [ $HTTPS_PROXY ]; then
    BUILD_ARGS+=" --build-arg HTTPS_PROXY=${HTTPS_PROXY}"
fi


function log_ts() {  # Log message with timestamp
    echo [DEBUG LOG at $(date -u +%Y%m%d:%H%M%S)] "$@"
}

function build_image() {
    log_ts Building Image in folder: $PWD with build arguments ${BUILD_ARGS}
    docker build ${BUILD_ARGS} -t ${IMAGE_NAME}:latest conductor/docker
    log_ts ... Built
}

function tag_image() {
    log_ts Tagging images: ${IMAGE_NAME}:\{$SNAPSHOT-${TIMESTAMP},$STAGING-${TIMESTAMP},latest\}
    docker tag ${IMAGE_NAME}:latest ${IMAGE_NAME}:${SNAPSHOT}-${TIMESTAMP}
    docker tag ${IMAGE_NAME}:latest ${IMAGE_NAME}:${STAGING}-${TIMESTAMP}
    docker tag ${IMAGE_NAME}:latest ${IMAGE_NAME}:latest
    log_ts ... Tagged images
}

function push_image(){
    log_ts Pushing images: ${IMAGE_NAME}:\{$SNAPSHOT-${TIMESTAMP},$STAGING-${TIMESTAMP},latest\}
    docker push ${IMAGE_NAME}:${SNAPSHOT}-${TIMESTAMP}
    docker push ${IMAGE_NAME}:${STAGING}-${TIMESTAMP}
    docker push ${IMAGE_NAME}:latest
    log_ts ... Pushed images
}

(
    build_image
    tag_image
    push_image
)
