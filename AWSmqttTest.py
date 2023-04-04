import paho.mqtt.client as mqtt
import ssl
import time
import json
import string
import random


host = 'azhp84fpfuib.iot.us-west-2.amazonaws.com'	#arnergy server
port = "8883"


def on_connect(client, userdata, flags, rc): #rc (return code) used to check what happend on connection
    if rc==0:
        client.connected_flag=True
        print 'connected with result code ' +str(rc)
        client.subscribe("data/warning/v3", qos=1)
        client.subscribe("data/mode/v3", qos=1)
        client.subscribe("data/parameters/v3", qos=1)
        client.subscribe("data/currentsettings/v3", qos=1)
	    #client.subscribe("$aws/things/416813/shadow/update/get/accepted", qos=0)
        #client.subscribe("$aws/things/416813/shadow/update/delta", qos=0)
	    #client.subscribe("data/generalstatus/v4", qos=1)
        #client.subscribe("data/power/v4", qos=1)
        client.subscribe("data/dashboard/v3", qos=1)
    else:
        logging.info('Bad connection with Returned code ' +str(rc))
        client.bad_connection_flag=True

def on_subscribe(client, userdata, mid, granted_qos):
    print 'Succesfully subscribed with QoS of %s', granted_qos
    time.sleep(1)
          
def on_publish(client,userdata,result):            
    print "published successfully"
    pass


def on_message(client, userdata, msg):
    if (msg.payload.find(ID) != -1): # or (msg.payload.find('41681784') != -1):
        print "******recieved "+ msg.topic+' '+ str(msg.payload)
    #tosearch = json.loads(msg.payload)
    #print "recieved "+ msg.topic+' '+str(tosearch)
    #if  tosearch['DeviceID'] == '41681784': #or tosearch['DeviceID'] == '41681784':
    #    print "recieved "+ msg.topic+' '+ str(msg.payload)

    
letters = string.ascii_lowercase
res =  ''.join(random.choice(letters) for i in range(10)) 

mqtt.Client.connected_flag=False 
mqtt.Client.bad_connection_flag=False 
client = mqtt.Client(client_id=res, clean_session=True)  
client.on_connect = on_connect
client.on_subscribe = on_subscribe
client.on_publish = on_publish
client.on_message = on_message

ID = raw_input("Enter system ID: ")
print "You have entered " + ID

client.tls_set("RootCA.pem", "certificate.pem.crt", "private.pem.key", tls_version=ssl.PROTOCOL_TLSv1_2)

try:
    print 'Attempting to connect to AWS'
    client.connect(host, port, 30)

except:
    print'cannot connect to network'

client.loop_start()
while True:
    print"In while loop"
    #client.publish('data', "publish test", qos=1)
    time.sleep(600)
