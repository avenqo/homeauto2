# Subscribing to Tibber Websocket and receiving updates from there.
# Publish the received data to MQTT Broker
#
import requests
import time
import calendar
import websockets
from libs.mqtt_pub import MqttPub
from libs.mqtt_topics import MQTT_TOPIC_TIBBER_PULSE_CONSUMPTION, MQTT_TOPIC_PRODUCTION
from gql import Client, gql
from gql.transport.websockets import WebsocketsTransport
from dateutil.parser import parse
import sys


class TibberPulse:
    """Read out power values provided by Tibber."""

    def __init__(self, urlTibber, key, mqtt_pub, logger):
        self.key = key
        self.urlTibber = urlTibber
        self.log = logger
        self.mqtt_pub = mqtt_pub
        self.subscription_query = """
            subscription {{
                liveMeasurement(homeId:"{HOME_ID}"){{
                    timestamp
                    power
                    powerProduction
                    accumulatedConsumption
                    accumulatedCost
                    voltagePhase1
                    voltagePhase2
                    voltagePhase3
                    currentL1
                    currentL2
                    currentL3
                    lastMeterConsumption
                }}
            }}
        """
        self.headers = {"Authorization": "Bearer " + key}

    def _run_query(self, query, headers):
        """A simple function to use requests.post to make the API call. Note the json= section."""

        request = requests.post(
            url=self.urlTibber, json={"query": query}, headers=headers
        )
        if request.status_code == 200:
            return request.json()
        else:
            raise Exception(
                "Query failed to run by returning code of {}. {}".format(
                    request.status_code, query
                )
            )

    def _ifStringZero(self, val):
        """Check if val is a valid digit. Return trimmed val OR None"""

        val = str(val).strip()
        if val.replace(".", "", 1).isdigit():
            res = float(val)
        else:
            res = None
        return res

    def initSocketUri(self):
        self.log.info("Tibber->initSocketUri()")

        # Get HomeID & WebSocket URI
        query = "{ viewer { homes { address { address1 } id } } }"
        resp = self._run_query(query, self.headers)
        self.tibberhomeid = resp["data"]["viewer"]["homes"][0]["id"]
        # currently not used
        self.address = resp["data"]["viewer"]["homes"][0]["address"]["address1"]

        # Get subscription URI
        resp = self._run_query("{viewer{websocketSubscriptionUrl}}", self.headers)
        self.ws_uri = resp["data"]["viewer"]["websocketSubscriptionUrl"]
        self.log.info(
            "Using homeid ["
            + self.tibberhomeid
            + "], adr ["
            + self.address
            + "], ws_uri ["
            + self.ws_uri
            + "]"
        )

    def fetch_data(self):
        self.log.info("Tibber->fetch_data()")

        transport = WebsocketsTransport(
            url=self.ws_uri, headers=self.headers, keep_alive_timeout=120
        )
        ws_client = Client(transport=transport, fetch_schema_from_transport=True)
        subscription = gql(self.subscription_query.format(HOME_ID=self.tibberhomeid))
        try:
            for result in ws_client.subscribe(subscription):
                self.log.info("Tibber->fetch_data(): result(" + str(result) + ")")
                self.console_handler(result)

        except (
            websockets.exceptions.ConnectionClosedError,
            ConnectionResetError,
        ) as ex1:
            module = ex1.__class__.__module__
            print(module + ex1.__class__.__name__)
            self.log.info("Connection was closed. Try to reconnecting ...")
            time.sleep(6)
            self.fetch_data()

        except Exception as ex:
            module = ex.__class__.__module__
            print(module + ex.__class__.__name__)
            exargs = str(ex.args)
            if exargs.find("Too many open connections") != -1:
                self.log.info("Too many open connections. Sleeping 10 minutes...")
                self.log.info(
                    "If you continue to see this error you can fix it by recreating the tibber token"
                )
                time.sleep(600)

            ws_client.transport.close()
            self.mqtt_pub.loop_stop()
            self.log.info("Finally: Client closed.")
            sys.exit(22)

    def console_handler(self, data):
        self.log.info("Tibber->console_handler()")

        if "liveMeasurement" in data:
            measurement = data["liveMeasurement"]
            timestamp = measurement["timestamp"]
            timeObj = parse(timestamp)
            hourMultiplier = timeObj.hour + 1
            daysInMonth = calendar.monthrange(timeObj.year, timeObj.month)[1]
            consumption = measurement["power"]
            production = measurement["powerProduction"]

            # min_power = measurement['minPower']
            # max_power = measurement['maxPower']
            # avg_power = measurement['averagePower']
            accumulated = measurement["accumulatedConsumption"]
            accumulated_cost = measurement["accumulatedCost"]
            # currency = measurement['currency']
            voltagePhase1 = measurement["voltagePhase1"]
            voltagePhase2 = measurement["voltagePhase2"]
            voltagePhase3 = measurement["voltagePhase3"]
            currentL1 = measurement["currentL1"]
            currentL2 = measurement["currentL2"]
            currentL3 = measurement["currentL3"]
            lastMeterConsumption = measurement["lastMeterConsumption"]
            # print(accumulated)
            output = [
                {
                    "measurement": "pulse",
                    "time": timestamp,
                    "tags": {"address": self.address},
                    "fields": {
                        "power": self._ifStringZero(consumption),
                        "consumption": self._ifStringZero(accumulated),
                        "cost": self._ifStringZero(accumulated_cost),
                        "voltagePhase1": self._ifStringZero(voltagePhase1),
                        "voltagePhase2": self._ifStringZero(voltagePhase2),
                        "voltagePhase3": self._ifStringZero(voltagePhase3),
                        "currentL1": self._ifStringZero(currentL1),
                        "currentL2": self._ifStringZero(currentL2),
                        "currentL3": self._ifStringZero(currentL3),
                        "lastMeterConsumption": self._ifStringZero(
                            lastMeterConsumption
                        ),
                        "hourmultiplier": hourMultiplier,
                        "daysInMonth": daysInMonth,
                    },
                }
            ]

            self.mqtt_pub.publish(MQTT_TOPIC_TIBBER_PULSE_CONSUMPTION, consumption)
            self.mqtt_pub.publish(MQTT_TOPIC_PRODUCTION, production)

            # print("---- Output, Date ----")
            # print(output)
            # print(data)

    def readPower(self):
        self.log.info("Tibber->readPower()")

        print("Sleep for 5 secs.")
        time.sleep(5)
        print("Run GQL query.")
        self.fetch_data()