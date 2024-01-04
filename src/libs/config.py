from configparser import ConfigParser
import os


class Config:
    def __init__(self, logger):
        self.log = logger
        self.parser = ConfigParser()

        self.cfgFileRelPath = os.getenv("VICMPP_CFG")  # None
        if self.cfgFileRelPath is None:
            self.cfgFileRelPath = "config/config.ini"
        self.log.info("Reading config file from [" + self.cfgFileRelPath + "]")
        self.parser.read(self.cfgFileRelPath)

        # sections
        self.sectionHardware = self.parser["hardware"]
        self.sectionPower = self.parser["power"]
        self.sectionMqtt = self.parser["mqtt"]
        self.sectionGridCharger = self.parser["grid_charger"]

    def _updateConfigFile(self):
        with open(self.cfgFileRelPath, "w") as configfile:
            self.parser.write(configfile)

    def show(self):
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
        return self.sectionHardware["IP_MULTIPLUS"]

    def getUrlEnergy(self):
        return self.sectionHardware["URL_ENERGY_METER"]

    # ----- Charge from Grid ------
    def getGridChargeSocLimitLow(self):
        return int(self.sectionGridCharger["GRID_CHARGER_SOC_LIMIT_LOW"])

    def setGridChargeSocLimitLow(self, value):
        self.sectionGridCharger["GRID_CHARGER_SOC_LIMIT_LOW"] = value
        self._updateConfigFile()

    def getGridChargeSocLimitHigh(self):
        return int(self.sectionGridCharger["GRID_CHARGER_SOC_LIMIT_HIGH"])

    def setGridChargeSocLimitHigh(self, value):
        self.sectionGridCharger["GRID_CHARGER_SOC_LIMIT_HIGH"] = value
        self._updateConfigFile()

    def getGridChargePriceLimitLow(self):
        return int(self.sectionGridCharger["GRID_CHARGER_PRICE_LIMIT_LOW"])

    def setGridChargePriceLimitLow(self, value):
        self.sectionGridCharger["GRID_CHARGER_PRICE_LIMIT_LOW"] = value
        self._updateConfigFile()

    def getGridChargePowerLimit(self):
        return int(self.sectionGridCharger["GRID_CHARGER_POWER_LIMIT"])

    def setGridChargePowerLimit(self, value):
        self.sectionGridCharger["GRID_CHARGER_POWER_LIMIT"] = value
        self._updateConfigFile()

    # ----- Multiplus ------
    def getSocLimitLow(self):
        return int(self.sectionPower["SOC_LIMIT_LOW"])

    def setSocLimitLow(self, value):
        self.sectionPower["SOC_LIMIT_LOW"] = value
        self._updateConfigFile()

    def getSocLimitHigh(self):
        return int(self.sectionPower["SOC_LIMIT_HIGH"])

    def setSocLimitHigh(self, value):
        self.sectionPower["SOC_LIMIT_HIGH"] = value
        self._updateConfigFile()

    def getGridSetPoint(self):
        return int(self.sectionPower["GRID_SETPOINT"])

    def setGridSetPoint(self, value):
        self.sectionPower["GRID_SETPOINT"] = value
        self._updateConfigFile()

    def getPowerChargeLimit(self):
        limit = int(self.sectionPower["MAX_POWER_CHARGE"])
        if limit > 0:
            limit *= -1
        return limit

    def setPowerChargeLimit(self, limit):
        if limit > 0:
            limit *= -1
        self.sectionPower["MAX_POWER_CHARGE"] = limit
        self._updateConfigFile()

    def getPowerInverterLimit(self):
        limit = int(self.sectionPower["MAX_POWER_INVERT"])
        if limit < 0:
            limit *= -1
        return limit

    def setPowerInverterLimit(self, limit):
        if limit < 0:
            limit *= -1
        self.sectionPower["MAX_POWER_INVERT"] = limit
        self._updateConfigFile()

    # ----- MQTT Broker ------
    def getMqttBrokerHost(self):
        return self.sectionMqtt["MQTT_BROKER_HOST"]

    def getMqttBrokerPort(self) -> int:
        return int(self.sectionMqtt["MQTT_BROKER_PORT"])
