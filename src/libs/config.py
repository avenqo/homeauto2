from configparser import ConfigParser
import os


class Config:
    def __init__(self, logger):
        self.log = logger
        self.parser = ConfigParser()

        cfgFileRelPath = os.getenv("VICMPP_CFG")  # None
        if cfgFileRelPath is None:
            cfgFileRelPath = "config/config.ini"
        self.log.info("Reading config file from [" + cfgFileRelPath + "]")
        self.parser.read(cfgFileRelPath)

        # sections
        self.cfgHardware = self.parser["hardware"]
        self.cfgPower = self.parser["power"]
        self.cfgMqtt = self.parser["mqtt"]

    def show(self):
        # dict1 = {}
        self.log.info("--- Current Config ---")
        for section in self.parser.sections():
            self.log.info("[" + section.title() + "]")
            options = self.parser.options(section)
            for option in options:
                try:
                    value = self.parser.get(section, option)
                    if value == -1:
                        self.log("skip Option: %s" % option)
                    else:
                        self.log.info("  " + option.title() + " = " + value)
                except:
                    self.log.exception("exception on Option %s!" % option)

        self.log.info("--- End of Config ---")

    # ----- Hardware ------
    def getMultiplusIp(self):
        return self.cfgHardware["IP_MULTIPLUS"]

    def getUrlEnergy(self):
        return self.cfgHardware["URL_ENERGY_METER"]

    # ----- Multiplus ------
    def getSocLimitLow(self):
        return int(self.cfgPower["SOC_LIMIT_LOW"])

    def getSocLimitHigh(self):
        return int(self.cfgPower["SOC_LIMIT_HIGH"])

    def getGridSetPoint(self):
        return int(self.cfgPower["GRID_SETPOINT"])

    def getPowerChargeLimit(self):
        limit = int(self.cfgPower["MAX_POWER_CHARGE"])
        if limit > 0:
            limit *= -1
        return limit

    def getPowerInverterLimit(self):
        limit = int(self.cfgPower["MAX_POWER_INVERT"])
        if limit < 0:
            limit *= -1
        return limit

    # ----- MQTT Broker ------
    def getMqttBrokerHost(self):
        return self.cfgMqtt["MQTT_BROKER_HOST"]

    def getMqttBrokerPort(self) -> int:
        return int(self.cfgMqtt["MQTT_BROKER_PORT"])
