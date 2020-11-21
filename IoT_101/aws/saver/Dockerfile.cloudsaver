# base image
FROM ubuntu

ENV DEBIAN_FRONTEND=noninteractive

# create working directory
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# install dependencies
RUN apt update && apt install -y libffi-dev python3-pip python3-tk libopencv-dev python3-opencv mosquitto-clients
RUN pip3 install paho-mqtt

# copy contents
#COPY saver.py /usr/src/app

