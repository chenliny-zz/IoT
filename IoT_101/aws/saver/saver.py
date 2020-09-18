import paho.mqtt.client as mqtt
import os.path
import cv2 as cv
import datetime
import numpy as np

# mqtt parameters
local_mqtt_host = "broker"
mqtt_port = 1883
mqtt_topic = "faces"

def on_connect_local(local_client, userdata, flags, rc):
    if rc == 0:
        #client.connected_flag = True
        print("Connected OK returned code = ", rc)
        local_client.subscribe(mqtt_topic, 1)
    else:
        print("Bad connection Returned code = ", rc)

def on_message(local_client, userdata, message):
    print("Receiving messages from edge device...")
    
    msg = message.payload
    timestamp = str(datetime.datetime.now()).replace(" ", "_")[:19]
    file_name = '/mnt/mountpoint/faces/face_{}.png'.format(timestamp)
    
    try:
        print("Decoding face image...")
        img = np.frombuffer(msg, dtype='uint8') 
        img_decoded = cv.imdecode(img, cv.COLOR_BGR2GRAY)
        cv.imwrite(file_name, img_decoded)
        print("Face captured with timestamp {} saved in object storage".format(timestamp))
        print("")
    except Exception as e:
        print("Error: {}".format(e))

# local and remote client instances
local_client = mqtt.Client("forwarder")

# bind call back function
local_client.on_connect = on_connect_local
local_client.on_message = on_message

# connect
local_client.connect(local_mqtt_host, mqtt_port, 60)

local_client.loop_forever()

