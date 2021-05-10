#!/usr/bin/env python3

import os
import subprocess
import json
import toml

from contextlib import suppress
from paho.mqtt.publish import single
from prometheus_client import start_http_server, Gauge, REGISTRY

import logging
logger = logging.getLogger()

# unregister the default promtheus process metrics
for name in list(REGISTRY._names_to_collectors.values()):
    with suppress(KeyError):
        REGISTRY.unregister(name)


def on_disconnect(*args, **kwargs):
    logger.info("client has disconnected")


def run():

    rtl433 = os.environ.get("RTL433")
    renix_cfg = os.environ.get("RENIXCFG", "/etc/renix.toml")

    # load config
    cfg = toml.load(renix_cfg)
    tire_positions = ['lf', 'rf', 'lr', 'rr']
    tire_map = {cfg['tpms'][position]: position for position in tire_positions}

    tire_pressure_g = Gauge('tire_pressure', 'Tire pressure', ['position', ])
    tire_temp_g = Gauge('tire_temperature', 'Tire temperature', ['position', ])
    cmd = [rtl433, "-f", "315M", "-F", "json", "-C", "customary"]

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
            single("tpms", json.dumps(data), client_id="tpms_monitor")

            # send to prometheus
            if 'pressure_PSI' in data:
                tire_pressure_g.labels(tire_position).set(data['pressure_PSI'])
            if 'temperature_F' in data:
                tire_temp_g.labels(tire_position).set(data['temperature_F'])


if __name__ == "__main__":

    # parser = argparse.ArgumentParser()
    # parser.add_argument('-p', '--prometheus', type=int, default=8080)

    start_http_server(8080)
    run()

    print("rtl 433 quit unexpectedly")
    exit(1)


