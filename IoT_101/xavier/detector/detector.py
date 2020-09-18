import numpy as np
import cv2 as cv
import paho.mqtt.client as mqtt
import time as time

# mqtt parameters
local_mqtt_host = 'broker'
mqtt_port = 1883
mqtt_topic = 'faces'

# global variable indicating disconnect status
dc_flag = False

# create callback functions
def on_connect_local(local_client, userdata, flags, rc):
    """
    This function handles the callback from the broker when it sends acknowledgement of connection status.
    """

    if rc == 0:
        local_client.connected_flag = True
        print("Connected OK returned code = ", rc)
    else:
        print("Bad connection Returned code = ", rc)

def on_disconnect_local(local_client, userdata, rc):
    #global dc_flag
    print("Disconnected due to ", rc)
    #dc_flag = True

# initiate local client instance
local_client = mqtt.Client("detector")

# connection flag indicating connection status
local_client.connected_flag = False

# bind call back functions
local_client.on_connect = on_connect_local
local_client.on_disconnect = on_disconnect_local

# loop start
local_client.loop_start()

# make connection
local_client.connect(local_mqtt_host, mqtt_port, 60)

while not local_client.connected_flag:
    print("Waiting in loop")
    time.sleep(1)

# create a face cascade object that loads the Haar Cascade file
face_cascade = cv.CascadeClassifier('/usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml')

# 1 should correspond to /dev/video1 , your USB camera.
# The 0 is reserved for the NX onboard camera or webcam on laptop
cap = cv.VideoCapture(0)

# capture video from camera
while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()

    # We don't use the color information, so might as well save space
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

    #### face detection logic
    # Use the detectMultiScale() method on the face_cascade
    # to generate a list of rectangles for all of the detected faces
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    # extract face
    for (x, y, w, h) in faces:
        frame = cv.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 5)
        face_extract = gray[y:y + h, x:x + w]
        rc, png = cv.imencode('.png', face_extract)
        msg = png.tobytes()
        #if dc_flag:
        #    local_client.connect(local_mqtt_host, mqtt_port, 60)
        local_client.publish(mqtt_topic, msg, qos=1, retain=False)

    cv.imshow('img', frame)
    if cv.waitKey(1) & 0xFF == ord('q'):
        break

# loop end
local_client.disconnect()

cap.release()
cv.destroyAllWindows()


