#!/bin/bash

# Build the docker image based on the saver Dockerfile
docker build -t saver -f Dockerfile.cloudsaver .

# launch
docker run --network iot101 --name saver --privileged -v /data:/data -v /mnt/mountpoint:/mnt/mountpoint -v /tmp:/tmp -ti saver
