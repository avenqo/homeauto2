from paho.mqtt import client as mqtt_client
import time

# for reconnection
FIRST_RECONNECT_DELAY = 1
RECONNECT_RATE = 2
MAX_RECONNECT_COUNT = 12
MAX_RECONNECT_DELAY = 60


class MqttPub:
    def __init__(self, broker, port, username, password, clientId, logger):
        self.broker = broker
        self.port = port
        self.username = username
        self.pwd = password
        self.clientId = clientId
        self.log = logger

    def connect_mqtt(self, startLoop=True):
        self.log.info("MqttPub->connect_mqtt()")

        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                self.log.info("Connected to MQTT Broker!")
            else:
                self.log.error("Failed to connect, return code %d\n", rc)

        # Set Connecting Client ID
        self.client = mqtt_client.Client(self.clientId)
        self.client.username_pw_set(self.username, self.pwd)
        self.client.on_connect = on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.connect(self.broker, self.port)
        if startLoop:
            self.client.loop_start()

    def publish(self, topic, msg):
        self.log.info("MqttPub->publish() - topic [%s], msg [%s]", topic, msg)
        result = self.client.publish(topic, msg)
        status = result[0]
        if status == 0:
            self.log.info(f"MqttPub->publish(): sent `{msg}` to topic `{topic}`")
        else:
            self.log.error(
                f"MqttPub->publish(): Failed to send message to topic {topic}"
            )

        """
        msg_count = 1
        while True:
            time.sleep(1)
            msg = f"messages: {msg_count}"
            result = self.client.publish(topic, msg)
            # result: [0, 1]
            status = result[0]
            if status == 0:
                print(f"Send `{msg}` to topic `{topic}`")
            else:
                print(f"Failed to send message to topic {topic}")
            msg_count += 1
            if msg_count > 5:
                break
        """

    def _on_disconnect(self, client, userdata, rc):
        self.log.info(
            "MqttPub->_on_disconnect() - Disconnected with result code: %s", rc
        )
        reconnect_count, reconnect_delay = 0, FIRST_RECONNECT_DELAY
        while reconnect_count < MAX_RECONNECT_COUNT:
            print("Reconnecting in %d seconds...", reconnect_delay)
            time.sleep(reconnect_delay)

            try:
                self.client.reconnect()
                self.log.info("Reconnected successfully!")
                return
            except Exception as err:
                self.log.err("%s. Reconnect failed. Retrying...", err)

            reconnect_delay *= RECONNECT_RATE
            reconnect_delay = min(reconnect_delay, MAX_RECONNECT_DELAY)
            reconnect_count += 1
        self.log.error(
            "Reconnect failed after %s attempts. Exiting...", reconnect_count
        )

    def loop_stop(self):
        self.log.info("MqttPub->loop_stop()")
        self.client.loop_stop

    def subscribe(self, topic, callback):
        def on_message(client, userdata, msg):
            print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")

        self.client.subscribe(topic)
        self.client.on_message = callback
