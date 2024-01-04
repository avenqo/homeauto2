# Recalc Victron Multiplus power


from libs.mp_modbus import MpModbus
from libs.config import Config
from libs.logConfig import initLogger
from timeit import default_timer as timer
import traceback
import sys

INTERVAL = 7  # loop interval in seconds
# Minimum house solar power to be delivered to grid
MIN_POWER = 100


class ControllMultiplus:
    def __init__(self, logger, config):
        self.log = logger
        self.cfg = config
        self.targetTime = timer() + INTERVAL
        self.multiPlus = MpModbus(
            self.cfg.getMultiplusIp(), logger=self.log, simulate=False
        )

    def recalc(
        self,
        TibberPower,
        EM24Power,
        VictronMpPower,
        Soc,
        VictronPvPower,
        SIMULATE=False,
    ):
        try:
            """Recalc Multiplus power control based on MQTT Events"""
            # ---- 1. Set new target time. Ignore system stressing events  -----
            if timer() < self.targetTime:
                # ignore calls being too early
                return
            self.targetTime = timer() + INTERVAL

            # ============== Calculate Multiplus (Dis-)Charge ==============
            HouseSolarPower = TibberPower - EM24Power
            # Power as needed by the house without the power consumed/provided by MultiPlus
            HouseNettoPower = EM24Power - VictronMpPower

            self.log.info(
                "Hauptkreis [W]\tBezug Tibber: %dW,\tEM24: %dW,\tHaus-Solar: %dW,\tHausNettoPower: %dW",
                TibberPower,
                EM24Power,
                HouseSolarPower,
                HouseNettoPower,
            )
            self.log.info(
                "Victron\tMPPT-Lader: %d W,\tMultiplus: %d W",
                VictronPvPower,
                VictronMpPower,
            )

            # ----- 4. Determine configs for Dis-/ Charge -----
            socLowLimit = self.cfg.getSocLimitLow()
            socHighLimit = self.cfg.getSocLimitHigh()
            if SIMULATE:
                watt = input("Enter Power: ")
                TibberPower = int(watt)
            self.log.info(
                "Battery\t\tSOC: %d,\tLimit low: %d,\tLimit high: %d",
                Soc,
                socLowLimit,
                socHighLimit,
            )

            # ----- 5. Calculate Victron -----
            victronMpPower = 0
            balance = HouseNettoPower + HouseSolarPower
            self.log.info("Balance (+..need, -..profit): %d W" % balance)

            # check for charging
            if (balance < 0) and (abs(balance) > MIN_POWER):
                # Keep balance smaller to ensure some minimum power consumption from grid
                victronMpPower = balance + MIN_POWER
                if victronMpPower < self.cfg.getPowerChargeLimit():
                    victronMpPower = self.cfg.getPowerChargeLimit()
                # Respect SOC level
                if Soc >= socHighLimit:
                    victronMpPower = 0
                    self.log.info(
                        "Not charging; SOC has reached upper limit [%d].", socHighLimit
                    )

                self.multiPlus.setControlledPower(victronMpPower)

            # check for discharging
            elif (balance > 0) and (
                balance > MIN_POWER
            ):  # power consumption is too high -> use excess for loading
                # hier fehlt noch VictronPv ?!
                # keep balance smaller to avoid energy delivery to grid
                victronMpPower = balance - MIN_POWER
                if victronMpPower > self.cfg.getPowerInverterLimit():
                    victronMpPower = self.cfg.getPowerInverterLimit()
                # Respect SOC level
                if (victronMpPower > 0) and (Soc < socLowLimit):
                    self.log.info(
                        "Not discharging; SOC [%d] is lower than lower SOC limit [%d]"
                        % (Soc, socLowLimit)
                    )
                    victronMpPower = 0
                self.multiPlus.setControlledPower(victronMpPower)
            else:
                self.multiPlus.activateIdle()

            # ---- 6. Ensure PV charger is  always ON -----
            # this is necessary; otherwise no loading will happen
            self.multiPlus.setDcPvChargerOn()

        except Exception as e:
            # try to close
            print(e)
            self.log.error("Exception occurred: " + str(e))
            traceback.print_exc()

            self.multiPlus.close()
            # emeter.close()

            self.log.debug("Reset loop")
            # multiPlus.activateIdle()
            TibberPower = 0
            targetTime = timer() + INTERVAL

            sys.exit(111)
