# base image
FROM alpine:latest

# create working directory
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# install dependencies
RUN apk add mosquitto py3-pip
RUN pip3 install paho-mqtt

# Copy contents
#COPY forwarder.py /usr/src/app
