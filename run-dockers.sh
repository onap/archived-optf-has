#!/bin/bash
### example run - provide the conductor configuration file as input to the run script
# ./run-dockers.sh <path-to>/conductor.conf

BUILD_ARGS="--no-cache"
ORG="onap"
VERSION="1.3.3"
PROJECT="optf-has"
DOCKER_REPOSITORY="nexus3.onap.org:10003"
IMAGE_NAME="${DOCKER_REPOSITORY}/${ORG}/${PROJECT}"

function print_usage {
    echo Usage:
    echo 1. conductor.conf file location
    echo 2. log.conf file location
    echo 3. AAI Certificate file location
    echo 4. AAI Key file location
    echo 5. AAI CA bundle file location  
}

function get_default_location(){
    [ -f "$1" ]               # run the test
    return $?                    # store the result
}

function get_from_arguments_or_default(){
    default_name=$1
    arg_num=$2
    echo $arg_num  argument $default_name file. Not provided 
    echo ... Trying to get using default name $default_name in current direcotry.

    get_default_location $default_name 
    if(($? == 0)); then
        echo ... Found $default_name in the current directory using this as $arg_num argument
        echo default_name is $arg_num
	if (($arg_num == 1)); then
	   COND_CONF=$(pwd)/$default_name
	elif (($arg_num == 2)); then
           LOG_CONF=$(pwd)/$default_name
 	elif (($arg_num == 3)); then
           CERT=$(pwd)/$default_name
 	elif (($arg_num == 4)); then
           KEY=$(pwd)/$default_name
	elif (($arg_num == 5)); then
           BUNDLE=$(pwd)/$default_name
        fi
    else
        echo ... Could not find $default_name in the location you are running this script from. Either provide as $arg_num argument to the script or copy as $default_name in current directory.
        print_usage
        exit 0;
    fi
}

#conductor.conf
if [ -z "$1" ]
  then
    get_from_arguments_or_default 'conductor.conf' 1 
fi

#log.conf
if [ -z "$2" ]
  then
    get_from_arguments_or_default 'log.conf' 2
fi

#aai_cert.cer
if [ -z "$3" ]
  then
    get_from_arguments_or_default './aai_cert.cer' 3
fi


#aai_key.key
if [ -z "$4" ]
  then
    get_from_arguments_or_default './aai_key.key' 4
fi


#aai_ca_bundle.pem
if [ -z "$5" ]
  then
    get_from_arguments_or_default './AAF_RootCA.cer' 5
fi

echo Value is .... $COND_CONF $LOG_FILE
echo Attempting to run multiple containers on image .... ${IMAGE_NAME}
docker login -u anonymous -p anonymous ${DOCKER_REPOSITORY}
docker run -d --name controller -v $COND_CONF:/usr/local/bin/conductor.conf -v $LOG_CONF:/usr/local/bin/log.conf ${IMAGE_NAME}:latest python /usr/local/bin/conductor-controller --config-file=/usr/local/bin/conductor.conf
docker run -d --name api -p "8091:8091" -v $COND_CONF:/usr/local/bin/conductor.conf -v $LOG_CONF:/usr/local/bin/log.conf ${IMAGE_NAME}:latest python /usr/local/bin/conductor-api --port=8091 -- --config-file=/usr/local/bin/conductor.conf
docker run -d --name solver -v $COND_CONF:/usr/local/bin/conductor.conf -v $LOG_CONF:/usr/local/bin/log.conf ${IMAGE_NAME}:latest python /usr/local/bin/conductor-solver --config-file=/usr/local/bin/conductor.conf
docker run -d --name reservation -v $COND_CONF:/usr/local/bin/conductor.conf -v $LOG_CONF:/usr/local/bin/log.conf ${IMAGE_NAME}:latest python /usr/local/bin/conductor-reservation --config-file=/usr/local/bin/conductor.conf
docker run -d --name data -v $COND_CONF:/usr/local/bin/conductor.conf -v $LOG_CONF:/usr/local/bin/log.conf -v $CERT:/usr/local/bin/aai_cert.cer -v $KEY:/usr/local/bin/aai_key.key -v $BUNDLE:/usr/local/bin/AAF_RootCA.cer ${IMAGE_NAME}:latest python /usr/local/bin/conductor-data --config-file=/usr/local/bin/conductor.conf

