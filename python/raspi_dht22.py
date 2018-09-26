### TOMOCON WORKSHOP 2018
#   Demo code
#   by Tomasz Cieplak
### ---------------------


import os
import time
import sys
import Adafruit_DHT as dht
import paho.mqtt.client as mqtt
import json

#MQTT_BROKER = 'test.mosquitto.org'
#MQTT_BROKER = 'iot.eclipse.org'
MQTT_BROKER = 'broker.hivemq.com'


# Data capture and upload interval in one second. Less interval will eventually hang the DHT22.
INTERVAL=1
sensor_data = {'temperature': 0, 'humidity': 0}
next_reading = time.time()
client = mqtt.Client("tomokon-001")

# The callback for when the client receives a CONNACK response from the server.
# 0: Connection successful 1: Connection refused - incorrect protocol version
# 2: Connection refused - invalid client identifier 3: Connection refused - server unavailable
# 4: Connection refused - bad username or password 5: Connection refused - not authorised

def on_connect(client, userdata, flags, rc):
    print("Connection returned result: {}".format(rc))

# When the message has been sent to the broker a callback will be generated.
def on_publish(client, userdata, result):
    print("Notification {} published! ".format(result))
    pass

# When client disconnected from the server
def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected disconnection.")


# Connect to broker using default MQTT port and 60 seconds keepalive interval
# Application of call back functions trigered with events

client.on_connect = on_connect
client.on_publish = on_publish
client.on_disconnect = on_disconnect

client.connect(MQTT_BROKER, 1883, 60)


client.loop_start()

try:
    while True:
        humidity,temperature = dht.read_retry(dht.DHT22, 22)
        humidity = round(humidity, 2)
        temperature = round(temperature, 2)
        print(u"Temperature: {:g}\u00b0C, Humidity: {:g}%".format(temperature, humidity))
        sensor_data['temperature'] = temperature
        sensor_data['humidity'] = humidity

        # Sending humidity and temperature data to ThingsBoard
        client.publish('tomocon/devices/telemetry', json.dumps(sensor_data), 1)

        next_reading += INTERVAL
        sleep_time = next_reading-time.time()
        if sleep_time > 0:
            time.sleep(sleep_time)
except KeyboardInterrupt:
    pass

client.loop_stop()
client.disconnect()
