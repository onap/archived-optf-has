### example run - provide the conductor configuration file as input to the run script
#./run-dockers.sh <path-to>/conductor.conf
docker run -v $1:/usr/local/bin/conductor.conf api & 
docker run -v $1:/usr/local/bin/conductor.conf controller &
docker run -v $1:/usr/local/bin/conductor.conf data &
docker run -v $1:/usr/local/bin/conductor.conf solver &
docker run -v $1:/usr/local/bin/conductor.conf reservation &
