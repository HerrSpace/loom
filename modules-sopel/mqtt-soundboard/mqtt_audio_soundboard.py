#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ✓

"""
mqtt_audio_soundboard.py - Search files by metadata in soundboard and put audio in mqtt message.
Copyright 2015, Patrick Meyer
"""

import os
import io
import threading
import json
from sopel.module import commands, priority
import mosquitto

from . import soundboard

MQTT_BROKER = os.environ.get('MQTT_BROKER') or "localhost"
SOUNDBOARD_MEDIA_PATH = os.path.dirname(os.path.realpath(__file__)) + "/soundboard_files/"

def setup(sopel_instance):
    mq_conn = mosquitto.Mosquitto()
    mq_conn.on_disconnect = on_mqtt_disconnect
    mq_conn.connect(host=MQTT_BROKER)
    sopel_instance.mq_conn = mq_conn
    mq_conn.user_data_set(sopel_instance)

    threading.Thread(target=mq_conn.loop_forever).start()

def on_mqtt_disconnect(mosq, sopel, rc):
    if rc != mosquitto.MOSQ_ERR_SUCCESS:
        print("MQTT disconnect: " + str(rc))
        time.sleep(1)
        print("MQTT reconnecting...")
        setup(sopel)

@commands('sob')
@priority('high')
def on_irc_msg(bot, trigger):
    print(trigger.group(2))
    index_path = soundboard._gen_index_path(SOUNDBOARD_MEDIA_PATH)
    with io.open(index_path, 'r', encoding='utf8') as json_fh:
        index = json.loads(json_fh.read())


    media_path = soundboard.single_search(trigger.group(2), index)[0]
    with io.open(SOUNDBOARD_MEDIA_PATH + media_path, 'rb') as audio_file:
        payload = bytearray(audio_file.read())

    bot._bot.mq_conn.publish("sob/audio", payload)
