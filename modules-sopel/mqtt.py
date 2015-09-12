# -*- coding: utf-8 -*-
# ✓

"""
mqtt.py - Sopel <-> MQTT bridge
Copyright 2015, Patrick Meyer
"""

MQ_HOST = "lux.z9"

import threading
import re
from sopel.module import rule, priority
import mosquitto

def setup(sopel_instance):
    mq_conn = mosquitto.Mosquitto()
    mq_conn.on_message = on_mqtt_message
    mq_conn.on_disconnect = on_mqtt_disconnect
    mq_conn.connect(host=MQ_HOST)
    sopel_instance.mq_conn = mq_conn
    mq_conn.subscribe(topic="msg/out/irc/+")
    mq_conn.user_data_set(sopel_instance)

    threading.Thread(target=mq_conn.loop_forever).start()

def on_mqtt_disconnect(mosq, sopel, rc):
    if rc != mosquitto.MOSQ_ERR_SUCCESS:
        print("MQTT disconnect: " + str(rc))
        time.sleep(1)
        print("MQTT reconnecting...")
        setup(sopel)

def on_mqtt_message(mosq, sopel, message):
    m = re.search(r"msg/out/irc/(.*)", message.topic)
    if not m: return
    dest = unescape_source(m.groups()[0])
    msg = message.payload.decode('utf-8')
    
    sopel.say(msg, dest)

@rule('.*')
@priority('high')
def on_irc_msg(bot, trigger):
    source = escape_source(trigger.sender)
    bot._bot.mq_conn.publish("msg/in/irc/"+source, trigger.group())

# +#/ <- These are magic character in mqtt topics, so we need to work around them.
def escape_source(source):
    return source.replace("#","😾").replace("+","☃").replace("/","🖕")
def unescape_source(source):
    return source.replace("😾","#").replace("☃","+").replace("🖕","/")
