#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ✓

"""
 - Play audio from MQTT
Copyright 2015, Patrick Meyer
"""

import io
import os
import subprocess
import uuid
import threading
import mosquitto

MQTT_BROKER = os.environ.get('MQTT_BROKER') or "localhost"


def setup():
    mq_conn = mosquitto.Mosquitto()
    mq_conn.on_message = on_mqtt_message
    mq_conn.on_disconnect = on_mqtt_disconnect
    mq_conn.connect(host=MQTT_BROKER)
    mq_conn.subscribe(topic="sob/audio")

    threading.Thread(target=mq_conn.loop_forever).start()

def on_mqtt_disconnect(mosq, _, rc):
    if rc != mosquitto.MOSQ_ERR_SUCCESS:
        print("MQTT disconnect: " + str(rc))
        time.sleep(1)
        print("MQTT reconnecting...")
        setup()

def on_mqtt_message(mosq, _, message):
    print(message.payload)
    tmp_file = "/tmp/" + str(uuid.uuid1())
    with io.open(tmp_file, 'wb') as fh:
        fh.write(message.payload)

    subprocess.call(["mpv", tmp_file])
    os.remove(tmp_file)



if __name__ == "__main__":
	setup()
