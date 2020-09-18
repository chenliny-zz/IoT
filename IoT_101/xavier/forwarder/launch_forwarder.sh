#!/bin/bash

# Build the docker image based on the detector Dockerfile
docker build -t forwarder .

# launch
docker run --network iot101 --name forwarder --privileged --runtime nvidia --rm -v /data:/data -v ${PWD}:/usr/src/app -ti forwarder
