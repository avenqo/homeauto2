from pymodbus.client import ModbusTcpClient as ModbusClient
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder, BinaryPayloadBuilder

UINT16 = 0
INT16 = 1

# For scanning go to Settings → Services → Modbus/TCP → Available services
# More infos here: https://www.victronenergy.com/live/ccgx:modbustcp_faq
UNIT_COMMON = 100
UNIT_MPLUS_VEBUS = 228
UNIT_SOLAR_CHARGER = 229    # Register 771 to 790
UNIT_GRID_METER = 30


class MpModbus:
    """Read Write Multiplus Modbus Registers in ESS Mode=3 (external control) and settings.
        Register 37: power, charger negative or inverter positive
        Register 38: charger enabled (0) or disabled (1)
        Register 39: inverter enabled (0) or disabled (1) 
    """

    def __init__(self, ip, logger, simulate=True):
        self.ip = ip
        self.log = logger
        self.simulate = simulate
        if simulate:
            self.log.info('--- Simulating Multiplus control ---')

    def _writeRegister(self, _unit, register,  value, typ):
        builder = BinaryPayloadBuilder(
            byteorder=Endian.Big, wordorder=Endian.Big)
        builder.reset()

        if typ == UINT16:
            builder.add_16bit_uint(value)
        elif typ == INT16:
            builder.add_16bit_int(value)
        else:
            raise NameError("Don't know how to handle type: " + str(typ))

        payload = builder.to_registers()
        self.client.write_register(register, payload[0], slave=_unit)

    def _readRegister(self, _unit, register,  typ, scale=1):

        result = self.client.read_input_registers(register, 1, slave=_unit)
        # https://pymodbus.readthedocs.io/en/v1.3.2/library/payload.html
        decoder = BinaryPayloadDecoder.fromRegisters(
            result.registers, byteorder=Endian.Big)
        if typ == UINT16:
            return decoder.decode_16bit_uint() / scale
        if typ == INT16:
            return decoder.decode_16bit_int()/scale
        raise NameError("Don't know how to handle type: " + str(typ))

    def showCurrentState(self):

        print('--- Current State ---')
        print("Set Point L1 : %d" %
              (self._readRegister(UNIT_MPLUS_VEBUS, 37, INT16)))
        print("Set Point L2 : %d" %
              (self._readRegister(UNIT_MPLUS_VEBUS, 40,  INT16)))
        print("Set Point L3 : %d" %
              (self._readRegister(UNIT_MPLUS_VEBUS, 41, INT16)))

     #   print("Disable Charge : %d" %
     #         (self._readRegister(UNIT_MULTI, 38 UINT16)))
        print("Disable Feed-in: %d" %
              (self._readRegister(UNIT_MPLUS_VEBUS, 39,  UINT16)))
        print("Disable overvoltage Feed-in : %d" %
              (self._readRegister(UNIT_MPLUS_VEBUS, 65,  UINT16)))

        print("Maximum Feed-in power due to overvoltage L1 : %d" %
              (self._readRegister(UNIT_MPLUS_VEBUS, 66,  UINT16)))
        print("Maximum Feed-in power due to overvoltage L2 : %d" %
              (self._readRegister(UNIT_MPLUS_VEBUS, 67,  UINT16)))
        print("Maximum Feed-in power due to overvoltage L3 : %d" %
              (self._readRegister(UNIT_MPLUS_VEBUS, 68,  UINT16)))
        print('--- END: Current State ---')

        # print("Power Setpoints acts as limit : %d" % (readRegister(71, 0)))
        # print("Overvoltage offset : %d" % (readRegister(72, 0)))

    def _open(self):
        self.client = ModbusClient(self.ip, port=502)

    def close(self):
        self.log.debug('Multiplus->close()')
        self.client.close()

    def getSoc(self):
        self.log.debug('Multiplus->getSoc()')
        self._open()
        soc = int(self._readRegister(UNIT_COMMON, 843, UINT16))
        self.close()
        return soc
    
    def setDcPvChargerOn(self):
        self.log.debug('MPPT Charger->setDcPvLoadOn()')
        self._open()
        # writeRegister(self, register, _unit, value, typ)
        self._writeRegister(UNIT_SOLAR_CHARGER, 774, 1, UINT16)
        self.close()
       
    def getDcPvPower(self):
        '''Power delivered by Victron Solar Charger'''
        self.log.debug('Multiplus->getDcPvPower()')
        self._open()
        # produced by PV
        #pv = int(self._readRegister(UNIT_COMMON, 850, UINT16))
        #pv = int(self._readRegister(UNIT_COMMON, 851, INT16))
        
        # ---- Battery ---
        batteryVoltage = int(self._readRegister(UNIT_SOLAR_CHARGER , 771, UINT16)) / 100
        self.log.debug('Battery Voltage: %d V' % batteryVoltage)
        batteryCurrent = int(self._readRegister(UNIT_SOLAR_CHARGER , 772, INT16)) / 10
        self.log.debug('Battery Current: %d' % batteryCurrent)
        batteryTemp = int(self._readRegister(UNIT_SOLAR_CHARGER , 773, INT16))
        self.log.debug('Battery Temperature : %d' % batteryTemp)
        
        batteryLoading = batteryVoltage * batteryCurrent
        self.log.debug(f'Battery Load Power : {batteryLoading}' )

#        #PV Voltage
#        pvVoltage = int(self._readRegister(UNIT_SOLAR_CHARGER , 776, UINT16)) / 100
#        self.log.debug('PV Voltage: %d' % pvVoltage)
#        #PV Current
#        pvCurrent = int(self._readRegister(UNIT_SOLAR_CHARGER , 777, INT16)) / 10
#        self.log.debug('PV Current: %d' % pvCurrent)
#        #PV Power; the Loading Power ist a little bit smaller
#        pvPower = int(self._readRegister(UNIT_SOLAR_CHARGER , 789, UINT16)) / 10
#        self.log.debug('PV Power: %d' % pvPower)
        
        pvStateString = "unknown"
        pvState = int(self._readRegister(UNIT_SOLAR_CHARGER , 775, UINT16))
        if pvState==0:
            pvStateString = "OFF"
        elif pvState == 2:
            pvStateString = "FAULT"
        elif pvState == 3:
            pvStateString = "BULK"
        elif pvState == 4:
            pvStateString = "ABSORPTION"
        elif pvState == 5:
            pvStateString = "FLOAT"
        elif pvState == 6:
            pvStateString = "STORAGE"
        elif pvState == 7:
            pvStateString = "EQUALIZE"
        elif pvState == 11:
            pvStateString = "OTHER"
        elif pvState == 252:
            pvStateString = "EXTERNAL CONTROL"
        self.log.debug('Solar Charger State: ' + pvStateString)


        self.close()
        return batteryLoading
    
    def getPowerConsumption(self):
        '''Power consumtion as read from EM24'''
        self.log.debug('Multiplus->getPowerConsumption()')
        self._open()
        L1 = int(self._readRegister(UNIT_COMMON, 820, INT16))
        self.log.debug('EM24 L1: %d W' % L1)
        L2 = int(self._readRegister(UNIT_COMMON, 821, INT16))
        self.log.debug('EM24 L2: %d W' % L2)
        L3 = int(self._readRegister(UNIT_COMMON, 822, INT16))
        self.log.debug('EM24 L3: %d W' % L3)
        self.close()
        return L1+L2+L3

    # -------------- Controlling Power -------------------- 

    def activateIdle(self):
        '''Power =0, but enable Charger and Inverter'''
        self.log.info('Multiplus->activateIdle()')
        self._writeControlledPower(0, 0, 0)

    def disableIdle(self):
        '''Disable Charger and Inverter'''
        self.log.info('Multiplus->disableIdle()')
        self._writeControlledPower(0, 1, 1)

    
    def setControlledPower(self, power):
        power = power * -1
        if power < -10:
            self.log.info('Multiplus->setControlledPower(%d W), discharging' % power)
            self._writeControlledPower(power)
        elif power > 10:
            self.log.info('Multiplus->setControlledPower(%d W), charging' % power)
            self._writeControlledPower(power)
        else:
            self.activateIdle()
    
    def getControlledPower(self):
        '''power > 0 => MP is charging, else: discharging'''
        self.log.debug('Multiplus->getPower()')
        self._open()
        soc = int(self._readRegister(UNIT_MPLUS_VEBUS, 37, INT16))
        self.close()
        return soc

    def _writeControlledPower(self, power, disableCharging=0, disableInverter=0):
        '''Default '0': Enable Charger and Inverter'''
        self.log.debug('Multiplus->_writeControlledPower(%d,%d,%d)' %
                       (power, disableCharging, disableInverter))
        self._open()
        # writeRegister(self, register, _unit, value, typ)
        self._writeRegister(UNIT_MPLUS_VEBUS, 37, power, INT16)
        self._writeRegister(UNIT_MPLUS_VEBUS, 38, disableCharging, UINT16)
        self._writeRegister(UNIT_MPLUS_VEBUS, 39, disableInverter, UINT16)
        self.close()
