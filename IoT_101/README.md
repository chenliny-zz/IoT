#### Pipeline components
![pipeline](/IoT_101/images/pipeline_v2.png)
- **Docker** is used to package all components as portable microservices.
- On the edge device, **Alpine Linux** is used as the base OS for the containers as it is frugal in terms of storage.
- For the edge detector component, **OpenCV** is used to scan the video frames coming from the connected USB camera. When one or more objects of interest are detected in the frame, the application would cut them out of the frame and send via a binary message to the cloud.
- **MQTT** is used as the messaging fabric. Therefore, an MQTT client is used to send and receive messages, and an MQTT broker is used as the server component of this architecture. Nvidia Jetson NX is used as an IoT Hub. Therefore, a local MQTT broker is installed in the NX, and the detector sends its messages to this broker first. Then, another component is developed to receive these messages from the local broker, and forwards them to the cloud.
- On the cloud, a **lightweight virtual machine** is provisioned and runs an MQTT broker; the images are published here as binary messages. Another component is created on the cloud to receive these binary files, decode them, and save them into object storage.

#### Launching and linking the microservices
[On the edge device (Nvidia Xavier NX)](https://github.com/chenliny/IoT/tree/master/IoT_101/xavier):
- MQTT mosquitto broker container (Alpine Linux based): This container acts as the broker on the edge device. Whenever the broker receives messages, it will place those messages into topics. Subscribers will then be able to obtain the messages from corresponding topics.
- Detector container: This container connects to the USB camera. It detects objects of interest and sends them to the internal mosquitto broker.
- MQTT forwarder container (Alpine Linux based): This container subscribes to the topics from the internal broker, fetches object files, and publishes them to the cloud mosquitto broker.
```
# Create local bridge network on edge device for broker, detector, and forwarder
docker network create --driver bridge iot101

# Build the docker image based on the edge broker Dockerfile
docker build -t broker -f /IoT_101/xavier/detector/Dockerfile.edgebroker .

# Build the docker image based on the detector Dockerfile
docker build -t detector -f /IoT_101/xavier/detector/Dockerfile.edgedetector .

# Build the docker image based on the forwarder Dockerfile
docker build -t forwarder -f /IoT_101/xavier/detector/Dockerfile.edgeforwarder .

# Enable X so that the container can output to a window
xhost +

# launch broker, detector, and forwarder
docker run -d --network iot101 --name broker -p 1883:1883 -ti broker mosquitto -v

docker run --network iot101 --name forwarder --privileged --runtime nvidia --rm -v /data:/data -v ${PWD}:/usr/src/app -ti forwarder

docker run --network iot101 --name detector --privileged --runtime nvidia --rm -v /data:/data -v ${PWD}:/usr/src/app -v /usr/share/opencv4/haarcascades:/usr/share/opencv4/haarcascades -e DISPLAY -v /tmp:/tmp -ti detector
```

[On the cloud (AWS)](https://github.com/chenliny/IoT/tree/master/IoT_101/aws):
- MQTT mosquitto broker container (Alpine Linux based): This container acts as the broker on the cloud. Whenever the broker receives messages, it will place those messages into topics. Subscribers will then be able to obtain the messages from corresponding topics.
- saver container: This container connects to the cloud mosquitto broker and acts as the image processor. It receives object messages, and places them into the object storage on the cloud.
```
# Create cloud bridge network for broker and saver
docker network create --driver bridge iot101

# Build the docker image based on the broker Dockerfile
docker build -t broker -f /IoT_101/aws/broker/Dockerfile.cloudbroker .

# Build the docker image based on the saver Dockerfile
docker build -t saver -f /IoT_101/aws/saver/Dockerfile.cloudsaver .

# launch broker and saver on the cloud
docker run -d --network iot101 --name broker -p 1883:1883 -ti broker mosquitto -v

docker run --network iot101 --name saver --privileged -v /data:/data -v /mnt/mountpoint:/mnt/mountpoint -v /tmp:/tmp -ti saver
```

To trigger the pipeline, execute a corresponding detector in the edge detector container.
