import sys

sys.path.append("../libs")
from pulse_reader import TibberPulse
from logConfig import initLogger
import os

TIBBER_URL = "https://api.tibber.com/v1-beta/gql"
# MQTT_BROKER_IP

log = initLogger()

TIBBER_API_TOKEN = os.getenv("TIBBER_API_TOKEN")  # None
if TIBBER_API_TOKEN is None:
    raise NameError("Environment variable TIBBER_API_TOKEN isn't defined yet!")

clientTibber = TibberPulse(TIBBER_URL, TIBBER_API_TOKEN, log)
clientTibber.initSocketUri()
clientTibber.readPower()
