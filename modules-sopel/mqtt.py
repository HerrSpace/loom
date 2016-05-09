#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ✓

"""
mqtt.py - Sopel <-> MQTT bridge
Copyright 2015, Patrick Meyer
"""

# TODO: Memory bridge

import os
import threading
import re
from sopel.module import rule, priority
import mosquitto

MQTT_BROKER = os.environ.get('MQTT_BROKER') or "localhost"

def setup(sopel_instance):
    mq_conn = mosquitto.Mosquitto()
    mq_conn.on_message = on_mqtt_message
    mq_conn.on_disconnect = on_mqtt_disconnect
    mq_conn.connect(host=MQTT_BROKER)
    sopel_instance.mq_conn = mq_conn
    mq_conn.subscribe(topic="msg/out/irc/+")
    mq_conn.user_data_set(sopel_instance)

    if not sopel_instance.memory.contains("loom"):
        sopel_instance.memory["loom"] = dict()

    threading.Thread(target=mq_conn.loop_forever).start()

def on_mqtt_disconnect(mosq, sopel, rc):
    if rc != mosquitto.MOSQ_ERR_SUCCESS:
        print("MQTT disconnect: " + str(rc))
        time.sleep(1)
        print("MQTT reconnecting...")
        setup(sopel)

def on_mqtt_message(mosq, sopel, message):
    m = re.search(r"msg/out/+/irc/(.*)", message.topic)
    if not m: return
    dest = unescape(m.groups()[0])
    msg = message.payload.decode('utf-8')
    
    sopel.say(msg, dest)

def _trigger_dict(trigger):
    # more or less the sopel trigger:
    # http://sopel.chat/docs/#the-trigger-class
    # TODO: include uflags from bot.privileges[trigger.sender][bot.nick]
    return {
        "admin": trigger.admin,
        "event": trigger.event,
        "host": trigger.host,
        "hostmask": trigger.hostmask,
        "is_privmsg": trigger.is_privmsg
        "nick": trigger.nick,
        "owner": trigger.owner,
        "raw": trigger.raw,
        "sender": trigger.sender,
        "tags": trigger.tags,
    }

@rule(r'!([^\s]+) (.*)')
@priority('high')
def on_irc_msg(bot, trigger):
    source = escape(trigger.sender)
    bot._bot.mq_conn.publish("cmd/irc/"+source+"/", trigger.group())

@rule(r'.*')
@priority('high')
def on_irc_msg(bot, trigger):

    mq_msq = _trigger_dict(trigger)
    mq_msq["msg"] = trigger.group()

    # TODO: log message
    bot._bot.mq_conn.publish("msg/in/irc/"+escape(trigger.sender), json.dumps(json_msg))

# +#/ <- These are magic character in mqtt topics, so we need to work around them.
def escape(source):
    return source.replace("#","😾").replace("+","☃").replace("/","🖕")
def unescape(source):
    return source.replace("😾","#").replace("☃","+").replace("🖕","/")
