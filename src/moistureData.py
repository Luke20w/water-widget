from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import logging
import time
import argparse
import json
import datetime
import random
from dateutil.tz import tzoffset

AllowedActions = ['both', 'publish', 'subscribe']

host = 'a3n2v7ltelt9xg-ats.iot.us-east-1.amazonaws.com'
rootCAPath = 'connect_device_package/root-CA.crt'
certificatePath = 'connect_device_package/AQI-IoT-Thing.cert.pem'
privateKeyPath = 'connect_device_package/AQI-IoT-Thing.private.key'
useWebsocket = False
clientId = 'basicPubSub'
topic = 'sdk/test/Python'

# Port defaults
if useWebsocket:  # When no port override for WebSocket, default to 443
    port = 443
if not useWebsocket:  # When no port override for non-WebSocket, default to 8883
    port = 8883

# Configure logging
'''
logger = logging.getLogger("AWSIoTPythonSDK.core")
logger.setLevel(logging.DEBUG)
streamHandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)
'''

# Init AWSIoTMQTTClient
myAWSIoTMQTTClient = None
if useWebsocket:
    myAWSIoTMQTTClient = AWSIoTMQTTClient(clientId, useWebsocket=True)
    myAWSIoTMQTTClient.configureEndpoint(host, port)
    myAWSIoTMQTTClient.configureCredentials(rootCAPath)
else:
    myAWSIoTMQTTClient = AWSIoTMQTTClient(clientId)
    myAWSIoTMQTTClient.configureEndpoint(host, port)
    myAWSIoTMQTTClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

# AWSIoTMQTTClient connection configuration
myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

# Connect and subscribe to AWS IoT
myAWSIoTMQTTClient.connect()

time.sleep(2)

loopCount = 0


def getData():
    messageJson={}
    plant=random.randint(0,4)
    if plant==0:
        messageJson['plantID']='plant0'
        #messageJson['location']='house1'
        messageJson['type']= 'agave' #0-20% water range
    elif plant==1:
        messageJson['plantID']='plant1'
        #messageJson['location']='house1'
        messageJson['type']= 'lavendar' #21-40% water range
    elif plant==2:
        messageJson['plantID']='plant2'
        #messageJson['location']='house2'
        messageJson['type']= 'daffodil' #21-60% water range
    elif plant==3:
        messageJson['plantID']='plant3'
        #messageJson['location']='house2'
        messageJson['type']= 'lupine' #41-60% water range
    elif plant==4:
        messageJson['plantID']='plant4'
        #messageJson['location']='house3'
        messageJson['type']= 'marsh marigold' #61-80% water range

    now=datetime.datetime.utcnow()
    messageJson['timestamp']=int(time.time())
    #messageJson['dataTime']=str(now.strftime("%Y-%m-%dT:%H:%M:%S"))
    messageJson['moisture']=random.randint(0,101)/10.0
    
    return messageJson

while True:        
    message = getData()
    messageJson = json.dumps(message)
    myAWSIoTMQTTClient.publish(topic, messageJson, 1)
    print('Published topic %s: %s\n' % (topic, messageJson))
    loopCount += 1
    time.sleep(1)
