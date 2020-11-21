#!/bin/bash

# Build the docker image based on the forwarder Dockerfile
docker build -t forwarder -f Dockerfile.edgeforwarder .

# launch
docker run --network iot101 --name forwarder --privileged --runtime nvidia --rm -v /data:/data -v ${PWD}:/usr/src/app -ti forwarder
