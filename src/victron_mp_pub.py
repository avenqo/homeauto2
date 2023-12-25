# Read Multiplus values and publish to MQTT Broker
# On exception -> close Multiplus and exit
from libs.logConfig import initLogger
from libs.config import Config
from libs.mp_modbus import MpModbus
from libs.mqtt_pub import MqttPub
from libs.mqtt_topics import *
from timeit import default_timer as timer
import traceback
import sys
import os

MQTT_CLIENT = "Victron_Publisher"

# ===== Init =====
INTERVAL = 3  # loop interval in seconds
targetTime = 0

# ----- Init: Logger -----
log = initLogger("./logs/victron.log")
cfg = Config(log)
cfg.show()

# ----- Init: MultiPlus -----
multiPlus = MpModbus(cfg.getMultiplusIp(), logger=log, simulate=False)

# ----- Init: MQTT Broker -----
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
mqttPublisher.connect_mqtt()


# --- Loop ---
# emeter = EnergyMeter(cfg.getUrlEnergy(), log)

while True:
    try:
        if timer() > targetTime:
            # Loop Control
            targetTime = timer() + INTERVAL
            log.info("LOOP")

            # ---- 0. Ensure PV charger is ON -----
            multiPlus.setDcPvChargerOn()

            # ---- 1. Read and publish  -----
            soc = multiPlus.getSoc()
            EValue = multiPlus.getPowerConsumption()
            VValue = multiPlus.getControlledPower()

            # sometimes None is returned
            VPvValue = -1
            anyVPvValue = multiPlus.getDcPvPower()
            if anyVPvValue is not None:
                VPvValue = -1 * int(multiPlus.getDcPvPower())

            log.info("Consumption\tE: %d W,\tV: %d W", EValue, VValue)
            log.info("Production\tVPv: %d W", VPvValue)
            log.info("Battery\t\tSOC: %d" % soc)

            mqttPublisher.publish(MQTT_TOPIC_EM24_CONSUMPTION, EValue)
            mqttPublisher.publish(MQTT_TOPIC_MP_POWER, VValue)
            mqttPublisher.publish(MQTT_TOPIC_MP_SOC, soc)
            mqttPublisher.publish(MQTT_TOPIC_MPPT_SOLAR_POWER, VPvValue)

    except Exception as e:
        # try to close
        log.error("Exception occurred: " + str(e))
        traceback.print_exc()
        multiPlus.close()
        sys.exit(111)
