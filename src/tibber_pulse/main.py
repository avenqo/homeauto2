import sys

from mqtt_pub import MqttPub
from pulse_reader import TibberPulse
from logConfig import initLogger
import os

# MQTT Broker
broker = "192.168.178.85"
port = 1883
topic = "home/kitchen/temperature"

TIBBER_URL = "https://api.tibber.com/v1-beta/gql"
# a readable name for the MQTT client
MQTT_CLIENT = "Tibber_Pulse_Publisher"

# Check ENV's
TIBBER_API_TOKEN = os.getenv("TIBBER_API_TOKEN")  # None
if TIBBER_API_TOKEN is None:
    raise NameError("Environment variable TIBBER_API_TOKEN isn't defined yet!")

MQTT_USER = os.getenv("MQTT_USER")  # None
if MQTT_USER is None:
    raise NameError(
        "Environment variable MQTT_USER isn't defined yet (user name for MQTT broker)!"
    )

MQTT_PWD = os.getenv("MQTT_PWD")  # None
if MQTT_PWD is None:
    raise NameError(
        "Environment variable MQTT_PWD isn't defined yet (password for MQTT broker)!"
    )

# Establish MQTT connection
log = initLogger()
mqttPublisher = MqttPub(broker, port, MQTT_USER, MQTT_PWD, MQTT_CLIENT, log)
# starts the loop too
mqttPublisher.connect_mqtt()

# Start websocket subscription
clientTibber = TibberPulse(TIBBER_URL, TIBBER_API_TOKEN, mqttPublisher, log)
clientTibber.initSocketUri()
# infinite loop
clientTibber.readPower()
