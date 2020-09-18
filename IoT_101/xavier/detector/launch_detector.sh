#!/bin/bash

# Build the docker image based on the detector Dockerfile
docker build -t detector .

# Enable X so that the container can output to a window.
xhost +

# launch
docker run --network iot101 --name detector --privileged --runtime nvidia --rm -v /data:/data -v ${PWD}:/usr/src/app -v /usr/share/opencv4/haarcascades:/usr/share/opencv4/haarcascades -e DISPLAY -v /tmp:/tmp -ti detector
