#!/usr/bin/env python3

from blinkstick import blinkstick
from tenacity import retry, stop_after_attempt, wait_fixed
from time import sleep

import argparse
import configparser
import copy
import paho.mqtt.client as mqtt
import os
import sys

def on_connect(client, userdata, flags, rc):
    global config
    print(f"Connected to MQTT broker with result code {rc}")
    client.subscribe(config['mqtt']['topic'])
    print(f"Subscribed to topic: '{config['mqtt']['topic']}'")

def on_message(client, userdata, msg):
    global color_ttl
    print(f"Message received [{msg.topic}]: {msg.payload}")
    color, ttl = str(msg.payload.decode("utf-8")).split(",")
    if ttl == 0:
        if color in color_ttl:
            del color_ttl[color]
    else:
        color_ttl[color] = int(ttl)

@retry(stop=stop_after_attempt(10), wait=wait_fixed(1))
def set_color(color):
    global device
    device.set_color(hex=color)

def parse_args():
    argsparser = argparse.ArgumentParser(
        description="Listen to MQTT topic(s) for colors to set a connected BlinkStick to"
    )
    argsparser.add_argument(
        "--config",
        "-c",
        default="config.ini",
        help="Specify the path to the configuration file (defaults to config.ini)",
    )

    return argsparser.parse_args()

def parse_config(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)
    return config

def startup_sequence_init():
    set_color("#220000")
    sleep(.5)
    set_color("#222200")
    sleep(.5)
    set_color("#002200")
    sleep(.5)

def startup_sequence_end():
    set_color("#000000")
    sleep(.2)
    set_color("#006600")
    sleep(.2)
    set_color("#000000")

def start_mqtt(mqtt_config):
    client = mqtt.Client(mqtt_config['clientID'])
    client.on_connect = on_connect
    client.on_message = on_message
    if all(key in mqtt_config for key in ("authUser","authPass")):
        client.username_pw_set(mqtt_config['authUser'], mqtt_config['authPass'])
    client.connect(mqtt_config['hostAddress'], int(mqtt_config['hostPort']))
    client.loop_start()

def do_loop(loop_config):
    global color_ttl

    loop_time = int(loop_config['duration'])
    while True:
        #print(color_ttl)
        for color, ttl in copy.copy(color_ttl).items():
            # If we get a message with a ttl of 0, immediately delete it and skip it in the loop
            if ttl <= 0:
                del color_ttl[color]
                continue
            set_color(color)
            new_ttl = ttl - loop_time
            if new_ttl <= 0:
                del color_ttl[color]
            else:
                color_ttl.update({color: new_ttl})
            sleep(loop_time)
        if len(color_ttl) == 0:
            set_color("#000000")
            sleep(1)

def main():
    global color_ttl, device, config

    args = parse_args()
    config = parse_config(args.config)

    device = blinkstick.find_first()
    if device == None:
        print("No BlinkStick found...")
        return 64

    startup_sequence_init()
    start_mqtt(config['mqtt'])
    startup_sequence_end()

    color_ttl = {}

    do_loop(config['loop'])

if __name__ == "__main__":
    sys.exit(main())
