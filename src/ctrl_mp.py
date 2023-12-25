# Recalc Victron Multiplus power
# Go on idle if no change was received for a minute

from libs.mp_modbus import MpModbus
from libs.config import Config
from libs.logConfig import initLogger
from timeit import default_timer as timer
import traceback
import sys

INTERVAL = 7  # loop interval in seconds


class ControllMultiplus:
    def __init__(self, logger):
        self.log = logger
        # self.parser = ConfigParser()
        self.cfg = Config(logger)
        self.targetTime = timer() + INTERVAL
        self.multiPlus = MpModbus(
            self.cfg.getMultiplusIp(), logger=self.log, simulate=False
        )

    # TValue -> Value from Tasmote/Tibber Pulse
    # EValue -> Value from EM24
    # VValue -> Power Value read from Multiplus

    def recalc(self, TValue, EValue, VValue, soc, VPvValue, SIMULATE=False):
        try:
            """Recalc Multiplus power control based on MQTT Events"""
            # ---- 0. Ensure PV charger is ON -----
            # this is necessary; otherwise no loading will happen
            self.multiPlus.setDcPvChargerOn()

            # ---- 1. Set new target time. Ignore system stressing events  -----
            if timer() < self.targetTime:
                # ignore calls being too early
                return
            self.targetTime = timer() + INTERVAL

            # ============== Calculate H(ausverbrauch), S(olar) ==============
            # H is the power as needed by the house without the power consumed/provided by MultiPlus
            SValue = TValue - EValue
            HValue = EValue - VValue

            # log.info("E: %d W" % EValue)
            # log.info("V: %d W" % VValue)
            # log.info("H: %d W" % HValue)

            self.log.info(
                "Consumption\tE: %d W,\tV: %d W,\tH: %d W", EValue, VValue, HValue
            )
            self.log.info("Production\tS: %d W,\tVPv: %d W", SValue, VPvValue)
            self.log.info("Battery\t\tSOC: %d" % soc)

            # ----- 4. Determine configs for Dis-/ Charge -----
            socLowLimit = self.cfg.getSocLimitLow()
            socHighLimit = self.cfg.getSocLimitHigh()
            if SIMULATE:
                watt = input("Enter Power: ")
                TValue = int(watt)

            # ----- 5. Calculate Victron -----
            chargerPower = 0

            bilanz = HValue + SValue
            self.log.info("Bilanz: %d W" % bilanz)
            if bilanz < -100:  # Bilanz negativ -> Es kann geladen werden!
                chargerPower = bilanz
                # Die Gesamtbilanz etwas im Minus Bereich halten, um so echten Verbrauch zu verhindern
                chargerPower += 100
                if chargerPower < cfg.getPowerChargeLimit():
                    chargerPower = cfg.getPowerChargeLimit()
                self.log.debug("Charger ON for %d W", chargerPower)

            elif bilanz > 100:  # Bilanz positiv -> Verbrauch ist zu hoch
                # hier fehlt noch VPv!
                chargerPower = bilanz
                # Etwas Eigenverbrauch ist sinnvoll, damit keine Akku Energie ins Netz geblasen wird.
                chargerPower -= 50
                self.log.debug("Inverter ON for %d W", chargerPower)
                if chargerPower > self.cfg.getPowerInverterLimit():
                    chargerPower = self.cfg.getPowerInverterLimit()
                #            else:
                #                chargerPower = 0
                #                log.info ("Multiplus IDLE schalten")

                # log.info("chargerPower %d ", chargerPower)
                # multiPlus.setControlledPower(int(chargerPower))

                #            log.info(
                #                "-> measurement: % d, powerBefore: %d,  power: %d"
                #                % (measurement, powerBefore, power)
                #            )
                #            powerBefore = power

                # log.info ("Inverter ON for %dW; soc=%d; socLowLimit=%d", chargerPower,soc, socLowLimit)
                # Respect SOC level
                if (chargerPower > 0) and (soc < socLowLimit):
                    self.log.info(
                        "SOC [%d] is lower than SOC-limit [%d]; ignoring requested invert mode: %dW"
                        % (soc, socLowLimit, chargerPower)
                    )
                    self.multiPlus.activateIdle()
                    chargerPower = 0
                elif (chargerPower < 0) and (soc > socHighLimit):
                    # log.info(   "Battery is full [%d] - loading canceled: %d W" % (soc, chargerPower))
                    self.log.info(
                        "SOC [%d] is higher than SOC-limit [%d]; ignoring requested charge mode: %dW"
                        % (soc, socHighLimit, chargerPower)
                    )
                    self.multiPlus.activateIdle()
                else:
                    self.multiPlus.setControlledPower(chargerPower)

        # except KeyboardInterrupt as e:
        #    exit()

        except Exception as e:
            # try to close
            print(e)
            self.log.error("Exception occurred: " + str(e))
            traceback.print_exc()

            self.multiPlus.close()
            # emeter.close()

            self.log.debug("Reset loop")
            # multiPlus.activateIdle()
            TValue = 0
            targetTime = timer() + INTERVAL

            sys.exit(111)
