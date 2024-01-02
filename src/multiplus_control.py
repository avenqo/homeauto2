# Subscribe on MQTT event and receive published values (Multiplus, EM24, Tibber, MPPT solar charger)
# Send the values to control_mp for recalculation
from libs.mqtt_pub import MqttPub
from libs.mqtt_topics import *
from libs.logConfig import initLogger
from libs.config import Config
from ctrl_mp import ControllMultiplus
from timeit import default_timer as timer
import sys
import os

# Max. wait until all measurements are available
TIMEOUT_SEC = 20
RECALC_INTERVAL_SEC = 5


class MqttEventHandler:
    def __init__(self, logger):
        self.log = logger


class MqttEventHandler:
    #  +: consumption, -: production
    TibberPower = None
    TibberProduction = None
    EM24Power = None
    VictronPvProduction = None
    Soc = None
    #  +: loading, -: supporting
    VictronMpPower = None

    def __init__(self, logger, config):
        self.log = logger
        self.cfg = config
        self.controllerMultiplus = ControllMultiplus(logger=logger, config=config)
        self.timeout = timer() + TIMEOUT_SEC
        # when should start the next recalculation
        self.nextRecalcTime = 0

    def onEvent(self, client, topic, value):
        if topic == MQTT_TOPIC_EM24_CONSUMPTION:
            self.EM24Power = int(value)
        elif topic == MQTT_TOPIC_MPPT_SOLAR_POWER:
            self.VictronPvProduction = int(value)
        elif topic == MQTT_TOPIC_MP_SOC:
            self.Soc = int(value)
        elif topic == MQTT_TOPIC_TIBBER_PULSE_CONSUMPTION:
            self.TibberPower = int(value)
        elif topic == MQTT_TOPIC_TIBBER_PULSE_PRODUCTION:
            self.TibberProduction = int(value)
        elif topic == MQTT_TOPIC_MP_POWER:
            self.VictronMpPower = int(value)
        # Configurations
        elif topic == MQTT_TOPIC_MP_CFG_SOC_LIMIT_LOW:
            strValue = str(value)
            self.cfg.setSocLimitLow(strValue)
            self.log.info("=== RECEIVED [" + MQTT_TOPIC_MP_CFG_SOC_LIMIT_LOW + "] ===")
            self.log.info("=== Value : [" + strValue + "]")
            self.log.info("=== Value2 : [" + str(self.cfg.getSocLimitLow()) + "]")

        elif topic == MQTT_TOPIC_MP_CFG_SOC_LIMIT_UPPER:
            self.cfg.setSocLimitHigh(value)
        elif topic == MQTT_TOPIC_MP_CFG_GRIDSETPOINT:
            self.cfg.setGridSetPoint(value)
        elif topic == MQTT_TOPIC_MP_CFG_MAX_POWER_INVERT:
            self.cfg.setPowerInverterLimit(int(value))
        elif topic == MQTT_TOPIC_MP_CFG_MAX_POWER_CHARGE:
            self.cfg.setPowerChargeLimit(int(value))

        else:
            self.log.error("Don't know how to handle [" + topic + "]")
        if self._isInitialized():
            if timer() > self.nextRecalcTime:
                self.controllerMultiplus.recalc(
                    self.TibberPower - self.TibberProduction,
                    self.EM24Power,
                    self.VictronMpPower,
                    self.Soc,
                    self.VictronPvProduction,
                )
                self.nextRecalcTime = timer() + RECALC_INTERVAL_SEC
        else:
            self.log.info("Waiting for measurement values ...")
            if timer() > self.timeout:
                self.log.error(
                    "Timeout when waiting for [" + str(TIMEOUT_SEC) + " sec.]"
                )
                sys.exit(3)

    def _isInitialized(self) -> bool:
        tibberPowerAvailable = self.TibberPower is not None
        tibberProductionAvailable = self.TibberProduction is not None
        em24PowerAvailable = self.EM24Power is not None
        victronPvProductionAvailable = self.VictronPvProduction is not None
        socAvailable = self.Soc is not None
        victronMpPowerAvailable = self.VictronMpPower is not None

        ret = (
            tibberPowerAvailable
            and tibberProductionAvailable
            and em24PowerAvailable
            and victronPvProductionAvailable
            and socAvailable
            and victronMpPowerAvailable
        )
        if not ret:
            msg = "Missing: "
            if not tibberPowerAvailable:
                msg += "Tibber Consumption Power, "
            if not tibberProductionAvailable:
                msg += "Tibber Production Power, "
            if not em24PowerAvailable:
                msg += "EM24 Power, "
            if not victronPvProductionAvailable:
                msg += "Victron PV Production Power, "
            if not socAvailable:
                msg += "SOC, "
            if not victronMpPowerAvailable:
                msg += "Victron Multiplus Power, "
            self.log.info(msg)
        return ret


# ================= MQTT EventHandler ========================
# --- Variable init ---
log = initLogger("./logs/ctrl_loop.log")
cfg = Config(log)
cfg.show()

mqttHandler = MqttEventHandler(log, cfg)

# --- On mqtt event handler ---


def onMqttEvent(client, userdata, msg):
    log.debug("MQTT event received")
    topic = msg.topic
    value = msg.payload.decode()
    mqttHandler.onEvent(client, topic, value)


# ===========================================================================
# --- MQTT connection & subscription ---
MQTT_CLIENT_NAME = "Multiplus_Control_Loop"

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
    MQTT_CLIENT_NAME,
    log,
)
# starts the loop too
mqttPublisher.connect_mqtt(False)

# Subscribe & loop
mqttPublisher.subscribe("/home/#", onMqttEvent)
mqttPublisher.client.loop_forever()
