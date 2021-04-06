#!/usr/bin/env python3

import subprocess
import json
import toml
import paho.mqtt.client as mqtt
from prometheus_client import start_http_server, Gauge

import logging
logger = logging.getLogger()


def run():

    # load config
    cfg = toml.load("/etc/renix.toml")
    tire_positions = ['lf', 'rf', 'lr', 'rr']
    tire_map = {cfg['tpms'][position]:position for position in tire_positions}

    # initialize clients
    mqttc = mqtt.Client("tpms_monitor")
    mqttc.connect("localhost", 1883)

    tire_pressure_g = Gauge('tire_pressure', 'Tire pressure', ['position', ])
    tire_temp_g = Gauge('tire_temperature', 'Tire temperature', ['position', ])
    cmd = ["/Users/amirsky/dev/rtl_433/build/src/rtl_433", "-f", "433M", "-F", "json"]

    rtl433 = subprocess.Popen(cmd, stdout=subprocess.PIPE)

    for line in iter(rtl433.stdout.readline, b''):

        data = None

        try:
            data = json.loads(line)
        except json.JSONDecodeError as e:
            print("could not decode json {}".format(line))

        if data['id'] not in tire_map:
            print("unrecognized tire id {}".format(data['id']))
        else:
            # send to mqtt
            tire_position = tire_map[data['id']]

            # augment the tpms data with tire location
            data['position'] = tire_position

            # send to mosquitto
            mqttc.publish("tpms", json.dumps(data))

            # send to prometheus
            if 'pressure_PSI' in data:
                tire_pressure_g.labels(tire_position).set(data['pressure_PSI'])
            if 'temperature_F' in data:
                tire_temp_g.labels(tire_position).set(data['temperature_F'])


if __name__ == "__main__":
    start_http_server(8080)
    run()

    print("rtl 433 quit unexpectedly")
    exit(1)


