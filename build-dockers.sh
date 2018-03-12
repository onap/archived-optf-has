#!/bin/bash
# TODO (IKRAM): need to test api only first to test the docker upload chain. 
# Will enable the others once api is tested
docker build -t api api/
docker build -t controller controller/
docker build -t data data/
docker build -t solver solver/
docker build -t reservation reservation/
