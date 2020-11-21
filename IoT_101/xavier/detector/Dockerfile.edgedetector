### detector container
# base image
FROM nvcr.io/nvidia/l4t-ml:r32.4.3-py3

# create working directory
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

RUN apt update && apt install -y libffi-dev python3-pip python3-tk libopencv-dev python3-opencv mosquitto-clients
RUN pip3 install paho-mqtt
