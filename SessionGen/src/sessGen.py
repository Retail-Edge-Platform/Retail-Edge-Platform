#!/usr/bin/env python3

from datetime import datetime, time, timedelta
import argparse
import random
import math
import json
import paho.mqtt.client as mqtt
import redis
import time as dtime
import os
import sys

from Session import Session

def applog(*a):
    print(*a, file = sys.stderr)

def poisson_distribution(k, lambd):
    """Modified from stackoverflow"""
    return (lambd ** k * math.exp(-lambd)) / math.factorial(k)

def is_time_between(begin_time, end_time, check_time=None):
    """Modified from stackoverflow"""
    # If check time is not given, default to current UTC time
    check_time = check_time or datetime.utcnow().time()
    if begin_time < end_time:
        return check_time >= begin_time and check_time <= end_time
    else: # crosses midnight
        return check_time >= begin_time or check_time <= end_time

class SimSessions(object):

    def __init__(self, start_datetime, end_datetime, prop_open_time, prop_close_time, avg_visits_per_hour):
        self.start_datetime = start_datetime
        self.end_datetime = end_datetime
        self.prop_open_time = prop_open_time
        self.prop_close_time = prop_close_time
        self.current_sim_datetime = start_datetime
        self.avg_visits_per_minute = float(avg_visits_per_hour)/60.0
        lambd = self.avg_visits_per_minute
        k = 1 # Looking ahead one minute at a time
        self.visit_prob = poisson_distribution(k, lambd)
        # Stores the event stream
        self.sesssions_stream = []
        # Defaults to 24 products to chose from
        self.number_of_products = 24

    def _is_visit_next_minute(self):
        # given a probability drawn from a poisson figure out if there is another visitor this minute
        visit_flip = random.uniform(0, 1) <= self.visit_prob 
        return visit_flip

    def _jump_to_open(self):
        """If the simualtion_time is in an time period where the shop is closed
        move the time ahead to when it would be open again."""
        # TODO: The clock is advanced on second at a time which may be ineffiecnt (backlog)
        check_time = self.current_sim_datetime.time()
        is_closed = True
        while is_closed:
            if is_time_between(self.prop_open_time, self.prop_close_time, check_time):
                #print("Yes - open")
                is_closed = False
            else:
                #print("No - closed")
                # If closed advance time until open
                self.current_sim_datetime += timedelta(seconds=1)
                check_time = self.current_sim_datetime.time()
                is_closed = True
        #print(self.current_sim_datetime)

    def _update_time_from_ms_epoch(self, timestamp):
        """When a session is completed it returns the amount of time it took. 
        This routine moves the simulation_time ahead."""
        sim_time_since_epoch = int(self.current_sim_datetime.timestamp() * 1000)
        delta_ms = timestamp - sim_time_since_epoch
        if delta_ms > 0:
            self.current_sim_datetime += timedelta(milliseconds=delta_ms)

    def _is_done(self):
        """Checks to see if the simualtion_time is outside of the 
        end datetime set from the CLI"""
        # Is the sim done ? 
        return self.current_sim_datetime > self.end_datetime

    def _advance_sim_time(self, minutes):
        """Convienent way to move forward the simulation_time."""
        self.current_sim_datetime += timedelta(minutes=minutes)

    def set_number_of_products(self, number_of_products):
        """Set the number of products that can be chosen"""
        self.number_of_products = number_of_products

    def _get_sim_ms_timestamp(self):
        """Gets the current simulation_time in milliseconds since the epoch"""
        return int(self.current_sim_datetime.timestamp() * 1000)

    def run_simulation(self):
        """Runs the full simulation to create the output stream"""
        while not self._is_done():
            self._jump_to_open()  # if closed will advance to next open period
            if self._is_done():
                # If advanced into after enddatetime
                break # Leave
            if self._is_visit_next_minute():
                start_of_sesssion_ms_time = self._get_sim_ms_timestamp()
                session = Session(start_of_sesssion_ms_time, self.number_of_products)
                ms_time_after_session, new_session_stream = session.get_session()
                # Move simulator clock forward
                self._update_time_from_ms_epoch(ms_time_after_session)
                # Add new sessions to stream
                self.sesssions_stream.extend(new_session_stream)
            else:
                # No visit this minute so advance time
                self._advance_sim_time(1.0)

    def get_stream(self):
        """After simulation returns full stream of sessions interaction events"""
        return self.sesssions_stream

def mqtt_connect():
    #Get IP Address of MQTT Broker. When in docker_compose 
    MQTT_IP_ADDRESS = os.getenv("MQTT_IP_ADDRESS", "localhost")
    MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
    # Open connection to redis here and store the client as a property of this object
    mqtt_client = mqtt.Client("admin")
    try:
        mqtt_client.connect(MQTT_IP_ADDRESS, MQTT_PORT)
        applog("MQTT CONNECTED")
        return mqtt_client
    except: # TODO: Handle this correctly
        applog(f"ERROR: Couldn't make connection with MQTT broker at {MQTT_IP_ADDRESS} on port {MQTT_PORT}")
        return None

def mqtt_output_stream(stream, mqtt_topic):
    mqtt_client = mqtt_connect() # Returns None if cant' connect
        
    if mqtt_client is not None:
        for interaction in stream:
            mqtt_message = json.dumps(interaction)
            ret = mqtt_client.publish(mqtt_topic, mqtt_message)
        applog("Output sent via MQTT")
    else:
        applog("ERROR: MQTT client didn't connect")
        exit(1)

def redis_connect():
    #Get IP Address of Redis Server. When in docker_compose 
    REDIS_IP_ADDRESS = os.getenv("REDIS_IP_ADDRESS", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
    # Open connection to redis here and store the client as a property of this object
    try:
        redis_client = redis.Redis(host=REDIS_IP_ADDRESS, port=REDIS_PORT, db=0)
        applog("REDIS CLIENT CREATED")
    except:
        redis_client = None
        applog(f"ERROR: Couldn't make connection with REDIS server at {REDIS_IP_ADDRESS} on port {REDIS_PORT}")
    return redis_client




def redis_output_stream(stream):
    redis_client = redis_connect() # Returns None if cant' connect
         
    if redis_client is not None:
        count = 0
        for interaction in stream:
            # format redis key
            list_to_join = []
            # TODO: Save these also in a redis tme series
            interaction["src-id"] = "sim"
            pref_order = ["src-id", "product-id", "product-name", "interaction-type", "timestamp"]
            for field in pref_order:
                list_to_join.extend([field, str(interaction[field])])
            # TODO:Should test that none of the items have the delimiter : in them
            entry_key = ':'.join(list_to_join)
            redis_client.set(entry_key, count)

            #********************************
            # ZADD this to a set to make searching by datetime easier
            score = int(interaction['timestamp'])
            scored_data = entry_key
            z_key = "sim_ts"
            redis_client.zadd(z_key, {scored_data: score})

            count += 1
            if count > 1000:
                applog("Only going to put in the first 1000")
                break
        applog("Output recorded in Redis")
    else:
        applog("ERROR: Redis client didn't connect")
        exit(1)


if __name__ == "__main__":
    """sessGen - builds a multi-day stream of sessions.  
    
    Sessions are made up of interaction events (see the Session module).

    sessGen has 3 CLI parameters that are needed:
    start_datetime - Start of stream interval. Format for this argument is: <DD/MM/YY-HH:MM> example: 11/6/21-19:46
    end_datetime - End of stream interval. Format for this argument is: <DD/MM/YY-HH:MM> example: 11/6/21-19:46
    avg_visits_per_hour - Average sessions per hour as float

    Output:
    Currently the output is stored in a JSON file called `stream.json`
    """
    # Parse the CLI
    parser = argparse.ArgumentParser(description='Create a session stream. From start DateTime to end DateTime')
    parser.add_argument('--start_datetime',
                        default='11/6/21-19:46',
                        help='Start of stream interval. Format for this argument is: <DD/MM/YY-HH:MM> example: 11/6/21-19:46')
    parser.add_argument('--end_datetime',
                        default='11/7/21-19:46',
                        help='End of stream interval. Format for this argument is: <DD/MM/YY-HH:MM> example: 11/6/21-19:46')
    parser.add_argument('--avg_visits_per_hour', type=float,
                        default=4.0,
                        help='Average sessions per hour as float.')
    args = parser.parse_args()

    output_to_use = os.getenv("OUTPUT_TO", "STDOUT")

    applog("OUTPUT TO", output_to_use)

    # Print received parameters
    print("Running session simulation:")
    print("\tStart DateTime", args.start_datetime)
    print("\tEnd DateTime", args.end_datetime)
    print("\tAverage Visits per hour", args.avg_visits_per_hour)

    # Attempt to parse if failure print help
    try:
        sdt = datetime.strptime(args.start_datetime, "%d/%m/%y-%H:%M")
    except:
        print("Start Date Failed to parse: ", args.start_datetime, "\n")
        parser.print_help()
        exit(1)

    try:
        edt = datetime.strptime(args.end_datetime, "%d/%m/%y-%H:%M")
    except:
        print("End Date Failed to parse: ", args.end_datetime, "\n")
        parser.print_help()
        exit(1)

    avg_visits_per_hour = args.avg_visits_per_hour

    # TODO: Should be feed from CLI args or from config file (backlog)
    prop_open_time = time(10,00)
    prop_close_time = time(21,00)

    # Do the simulation
    sim_sesssions = SimSessions(sdt,edt,prop_open_time, prop_close_time, avg_visits_per_hour)
    # TODO: Get from config file or CLI args (backlog)
    sim_sesssions.set_number_of_products(23)
    sim_sesssions.run_simulation()

    # Get simulation stream
    stream = sim_sesssions.get_stream()


    if output_to_use == 'MQTT':
        mqtt_topic = os.getenv("MQTT_TOPIC", "/ui-stream")
        mqtt_output_stream(stream, mqtt_topic)

    elif output_to_use == 'REDIS_DB':
        redis_output_stream(stream)

    if output_to_use == 'STDOUT':
        # Save to file for now
        with open('stream.json', 'w') as ofh:
            json.dump(stream,ofh, indent=4, sort_keys=True)

        applog()
        applog("Output can be found in 'stream.json'")


    applog("Simulation finished. Exiting cleanly")

    exit(0)




