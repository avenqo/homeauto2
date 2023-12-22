# Victron Multiplus - Reading and publishing
## Goal
The idea of the module is to read Victron Multiplus values and connected devices like Victron MPPT.
The read values are taken and published to a MQTT broker

## Published messages
Power consumption as measured by EM24
/home/victron/em24/consumption

Power controlled by Victron Multiplus II -> positiv: charging, negative: discharging
/home/victron/mp/power/controlled

Battery state of charge
/home/victron/mp/battery/soc

MPPT Charger power
/home/victron/mppt/power
