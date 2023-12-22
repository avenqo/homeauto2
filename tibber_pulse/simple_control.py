# from lib.energy_meter import EnergyMeter
from libs.mp_modbus import MpModbus
from libs.config import Config
from libs.logConfig import initLogger
from timeit import default_timer as timer
import traceback
import sys

# ========== Constants ===========
# ----- inner configs -----
INTERVAL = 10  # loop interval in seconds

# limit runtime
cntLoop = 0
SIMULATE = False

# =========== Main =============
print("=== START loop ===")

# power = 0  # last set power value; negative -> charge
# powerBefore = 0
targetTime = 0
timerStart = 0
log = initLogger()
log.info("=== (Re-) Starting Victron Control Loop ===")

cfg = Config(log)
cfg.show()

multiPlus = MpModbus(cfg.getMultiplusIp(), logger=log, simulate=SIMULATE)
# emeter = EnergyMeter(cfg.getUrlEnergy(), log)

while True:
    TValue = 0
    try:
        if timer() > targetTime:
            # ============== Loop Control ==============
            # ---- 0. Ensure PV charger is ON -----
            multiPlus.setDcPvChargerOn()

            # ---- 1. Adapt charger / inverter per interval -----
            targetTime = timer() + INTERVAL
            cntLoop -= 1
            print("--- LOOP " + str(cntLoop) + " ---")
            if cntLoop == 0:
                break

            # ============== Read measurements ==============
            # ---- 2. Tasmota: Determine power consumption (TValue) provided by Tasmota -----
            consumptionStr = emeter.readConsumption()
            if consumptionStr is not None:
                consumptionStr = consumptionStr.replace(" W", "")
                # measurement is the summarized(!) consumption -> try to balance
                TValue = int(consumptionStr)
                log.info("Tasmota: %d W  (SML Aktueller Verbrauch)" % TValue)

            # ----- 3. Multiplus: Determine SOC, M(ultiplus Power), E(M24), T(asmota) -----
            soc = multiPlus.getSoc()
            EValue = multiPlus.getPowerConsumption()
            VValue = multiPlus.getControlledPower()
            VPvValue = -1 * int(multiPlus.getDcPvPower())
            # Unklar welche Rolle VPv spielt. Kann ich im Inverterbetrieb sein und gleichzeitig laden?
            # Dann spielt Vpv evtl. keine Rolle!

            # ============== Calculate H(ausverbrauch), S(olar) ==============
            # H is the power as needed by the house without the power consumed/provided by MultiPlus
            SValue = TValue - EValue
            HValue = EValue - VValue

            # log.info("E: %d W" % EValue)
            # log.info("V: %d W" % VValue)
            # log.info("H: %d W" % HValue)

            log.info("Consumption\tE: %d W,\tV: %d W,\tH: %d W", EValue, VValue, HValue)
            log.info("Production\tS: %d W,\tVPv: %d W", SValue, VPvValue)
            log.info("Battery\t\tSOC: %d" % soc)

            # ----- 4. Determine configs for Dis-/ Charge -----
            socLowLimit = cfg.getSocLimitLow()
            socHighLimit = cfg.getSocLimitHigh()
            if SIMULATE:
                watt = input("Enter Power: ")
                TValue = int(watt)

            # ----- 5. Calculate Victron -----
            chargerPower = 0

            bilanz = HValue + SValue
            log.info("Bilanz: %d W" % bilanz)
            if bilanz < -100:  # Bilanz negativ -> Es kann geladen werden!
                chargerPower = bilanz
                # Die Gesamtbilanz etwas im Minus Bereich halten, um so echten Verbrauch zu verhindern
                chargerPower += 100
                if chargerPower < cfg.getPowerChargeLimit():
                    chargerPower = cfg.getPowerChargeLimit()
                log.debug("Charger ON for %d W", chargerPower)

            elif bilanz > 100:  # Bilanz positiv -> Verbrauch ist zu hoch
                # hier fehlt noch VPv!
                chargerPower = bilanz
                # Etwas Eigenverbrauch ist sinnvoll, damit keine Akku Energie ins Netz geblasen wird.
                chargerPower -= 50
                log.debug("Inverter ON for %d W", chargerPower)
                if chargerPower > cfg.getPowerInverterLimit():
                    chargerPower = cfg.getPowerInverterLimit()
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
                log.info(
                    "SOC [%d] is lower than SOC-limit [%d]; ignoring requested invert mode: %dW"
                    % (soc, socLowLimit, chargerPower)
                )
                multiPlus.activateIdle()
                chargerPower = 0
            elif (chargerPower < 0) and (soc > socHighLimit):
                # log.info(   "Battery is full [%d] - loading canceled: %d W" % (soc, chargerPower))
                log.info(
                    "SOC [%d] is higher than SOC-limit [%d]; ignoring requested charge mode: %dW"
                    % (soc, socHighLimit, chargerPower)
                )
                multiPlus.activateIdle()
            else:
                multiPlus.setControlledPower(chargerPower)

    # except KeyboardInterrupt as e:
    #    exit()

    except Exception as e:
        # try to close
        print(e)
        log.error("Exception occurred: " + str(e))
        traceback.print_exc()

        multiPlus.close()
        emeter.close()

        log.debug("Reset loop")
        # multiPlus.activateIdle()
        TValue = 0
        targetTime = timer() + INTERVAL

        sys.exit(111)


print("==== END ====")
multiPlus.activateIdle()
