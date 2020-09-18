import paho.mqtt.client as mqtt
import os.path

# mqtt parameters
local_mqtt_host = "broker"
mqtt_port = 1883
mqtt_topic = "faces"
remote_mqtt_host = "00.00.000.0" 

# global variable indicating disconnect status
#dc_flag = False

# create callback functions
def on_connect_local(local_client, userdata, flags, rc):
    """
    This function handles the callback from the local broker when it sends acknowledgement of connection status.
    """
    if rc == 0:
        local_client.connected_flag = True
        print("Connected local OK returned code = ", rc)
        local_client.subscribe(mqtt_topic)
    else:
        print("Bad connection local Returned code = ", rc)

def on_connect_remote(remote_client, userdata, flags, rc):
    """
    This function handles the callback from the cloud broker when it sends acknowledgement of connection status.
    """
    if rc == 0:
        remote_client.connected_flag = True
        print("Connected remote OK returned code = ", rc)
    else:
        print("Bad connection remote Returned code = ", rc)

def on_disconnect_remote(remote_client, userdata, rc):
    global dc_flag
    print("Disconnected due to ", rc)
    dc_flag = True

def on_message(client, userdata, message):
    """
    This function handles the callback from the local broker when it sends acknowledgement of messaging status. Upon receiving messages from the local broker, it then forwards those messages to the remote broker.
    """
    #global dc_flag

    try:
        print("Receiving messages")
        msg = message.payload

        #if dc_flag:
            #remote_client.connect(remote_mqtt_host, mqtt_port, 60)
        remote_client.publish(mqtt_topic, payload=msg, qos=0, retain=False)
    except:
        print("Error in receiving messages")

# create client object for local and remote
local_client = mqtt.Client("forwarderLocal")
remote_client = mqtt.Client("forwarderRemote")

# connection flag indicating connection status
local_client.connected_flag = False
remote_client.connected_flag = False

# bind callback to callback function
local_client.on_connect = on_connect_local
remote_client.on_connect = on_connect_remote
local_client.on_message = on_message
remote_client.on_disconnect = on_disconnect_remote

# connect to broker
local_client.connect(local_mqtt_host, mqtt_port, 60)
remote_client.connect(remote_mqtt_host, mqtt_port, 60)

# start a loop and loop forever
local_client.loop_forever()
