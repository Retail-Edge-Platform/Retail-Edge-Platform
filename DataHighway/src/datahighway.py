#!/usr/bin/env python3
import json
import redis
import paho.mqtt.client as mqtt
import time
import os
import sys

"""Datahighway is a bridge between REDIS pubsub and MQTT pubsub. 
While REDIS is good on the same platform it lacks security features that
have found their way into MQTT.

To use create two lists one of REDIS topics the service should listen to. 
The other a list topics that MQTT should publish to. Messages that come from
Redis are republished on MQTT.

There are four environmental variables that can be used to modify the behavior
of the datahighway connectivity.

        REDIS_IP_ADDRESS = os.getenv("REDIS_IP_ADDRESS", "localhost")
        REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

        MQTT_IP_ADDRESS = os.getenv("MQTT_IP_ADDRESS", "localhost")
        MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))

This is setup so that in a docker_compose file the IP address of one service 
can be feed to others.
"""

def applog(*a):
    print(*a, file = sys.stderr)


class DataHighway(object):
    def __init__(self, redis_listen_topics, mqtt_speak_topics):
        self.redis_listen_topics = redis_listen_topics
        self.mqtt_speak_topics  = mqtt_speak_topics
        self.mqtt_client = None
        self.redis_client = None

    def _connect(self):
        if self.redis_client is None:
            self._connect_redis()
        if self.mqtt_client is None:
            self._connect_mqtt()

    def _connect_redis(self):
        #Get IP Address of Redis Server. When in docker_compose 
        REDIS_IP_ADDRESS = os.getenv("REDIS_IP_ADDRESS", "localhost")
        REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
        # Open connection to redis here and store the client as a property of this object
        self.redis_client = redis.Redis(host=REDIS_IP_ADDRESS, port=REDIS_PORT, db=0)
        self.pubsub_hdl = self.redis_client.pubsub(ignore_subscribe_messages=True)
        for redis_topic in self.redis_listen_topics:
            self.pubsub_hdl.subscribe(redis_topic)
        applog("REDIS CONNECTED")
        
    def _connect_mqtt(self):
        #Get IP Address of MQTT Broker. When in docker_compose 
        MQTT_IP_ADDRESS = os.getenv("MQTT_IP_ADDRESS", "localhost")
        MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
        # Open connection to redis here and store the client as a property of this object
        self.mqtt_client = mqtt.Client("admin")
        try:
            self.mqtt_client.connect(MQTT_IP_ADDRESS, MQTT_PORT)
            applog("MQTT CONNECTED")
        except: # TODO: Handle this correctly
            print(f"ERROR: Couldn't make connection with MQTT broker at {MQTT_IP_ADDRESS} on port {MQTT_PORT}")

    def run_service(self, delay=1):
        self._connect()
        while True:
            
            redis_message = self.pubsub_hdl.get_message()  # Non-blocking read REDIS messages
            if redis_message and redis_message['type'] == 'message':
                # TODO: Needs a try except handler around it
                data = json.loads(redis_message['data'])
                mqtt_message = json.dumps(data)
                for mqtt_topic in self.mqtt_speak_topics:
                    # publish MQTT messsages
                    ret= self.mqtt_client.publish(mqtt_topic, mqtt_message)
                    applog("MQTT Sent", mqtt_message)
            time.sleep(delay)

if __name__ == "__main__":
    
    redis_topic_list = ['ui-stream']
    mqtt_topic_list = ['/ui-stream']

    bridge = DataHighway(redis_topic_list, mqtt_topic_list)
    # TODO: There should be a kill handler to gracefully shutdown when docker asks
    bridge.run_service()  # Won't return from this loop until killed