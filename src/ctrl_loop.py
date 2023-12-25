# Subscribe on MQTT event
# Delegate Events to Multiplus control
from libs.mqtt_pub import MqttPub
from libs.mqtt_topics import *
from libs.logConfig import initLogger
from libs.config import Config
from ctrl_mp import ControllMultiplus

# from libs.mp_modbus import MpModbus
import os

# --- Variable init ---
log = initLogger("./logs/ctrl_loop.log")
cfg = Config(log)
cfg.show()

# multiPlus = MpModbus(cfg.getMultiplusIp(), logger=log, simulate=SIMULATE)
controllerMultiplus = ControllMultiplus(logger=log)

# --- Handle MQTT Events ---
# powerConsumtion = 0


TValue = ""
EValue = 0
VPvValue = 0
soc = 0
VValue = 0


def onMqttEvent(client, userdata, msg):
    global TValue
    global TProductionValue
    global EValue
    global VPvValue
    global soc
    global VValue

    topic = msg.topic
    value = msg.payload.decode()

    if topic == MQTT_TOPIC_EM24_CONSUMPTION:
        EValue = int(value)
    elif topic == MQTT_TOPIC_MPPT_SOLAR_POWER:
        VPvValue = int(value)
    elif topic == MQTT_TOPIC_MP_SOC:
        soc = int(value)
    elif topic == MQTT_TOPIC_TIBBER_PULSE_CONSUMPTION:
        TValue = int(value)
    elif topic == MQTT_TOPIC_TIBBER_PULSE_PRODUCTION:
        TProductionValue = int(value)
    elif topic == MQTT_TOPIC_MP_POWER:
        VValue = int(value)
    elif topic.startswith("/home/house/"):
        z = 0  # nothing
    else:
        log.error("Dont know how to handle topic [%s].", topic)

    print(f"MQTT Event: `{msg.payload.decode()}` from `{msg.topic}` topic")
    controllerMultiplus.recalc(TValue, EValue, VValue, soc, VPvValue)

    # --- publish measured and calculated results ---
    # House Solar System Production
    try:
        log.info("value [%s], EValue [%s], TValue [%s]", value, EValue, TValue)
        mqttPublisher.publish(MQTT_TOPIC_HOUSE_SOLAR_PROD, EValue - TValue)
        # Devices consuming energy (or producing e.g. balkony solar systems)
        mqttPublisher.publish(MQTT_TOPIC_HOUSE_CONSUMPTION, EValue - VValue)
        # mqttPublisher.publish(MQTT_TOPIC_HOUSE_CO, EValue - VValue)
    except TypeError:
        log.info("Cancel result publishing due to TypeError")


# --- MQTT connection & subscription ---
MQTT_CLIENT = "Control_Loop"

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

mqttPublisher = MqttPub(
    cfg.getMqttBrokerHost(),
    cfg.getMqttBrokerPort(),
    MQTT_USER,
    MQTT_PWD,
    MQTT_CLIENT,
    log,
)
# starts the loop too
mqttPublisher.connect_mqtt(False)

# Subscribe & loop
mqttPublisher.subscribe("/home/#", onMqttEvent)

# Sometimes: TypeError: _on_disconnect() takes 3 positional arguments but 4 were given
# This has to do with MQTT versions?!

mqttPublisher.client.loop_forever()
