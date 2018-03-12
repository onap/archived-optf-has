#!/bin/bash
# TODO (IKRAM): need to test api only first to test the docker upload chain. 
# Will enable the others once api is tested
docker build -t api conductor/docker/api/
docker build -t controller conductor/docker/controller/
docker build -t data conductor/docker/data/
docker build -t solver conductor/docker/solver/
docker build -t reservation conductor/docker/reservation/
