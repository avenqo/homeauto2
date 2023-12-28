# Home Automation
This project represents the home automation control running on Raspberry PI for a configuration based on 
- LiFePo battery and balancer
- multiple solar chargers
- Victron Multiplus (in ESS mode)

A special condition is the fact that the "House Solar" system was created in 2008. The related SMA inverter are not able to communicate with the rest of system. Therfore, the current amount of solar production must be derived from grid meter and EM24 measurement.

[ToDo's](doc/todos.md)
## Goal
The main goal is 
1. to avoid power consumption from grid by solar charging  and using the battery power
2. to achieve the lowest electrical energy price especially at winter time by (nightly) charging the battery via Tibber

## Overview
### System overview
![architecture](./doc/drawings/system_overview.png).
### Measurements
![measurements](./doc/drawings//energy_calculation.png).
## Necessary Tools & Libraries
### Mosquitto (MQTT Server)
The MQTT server is the information broker in the middle of the system.
Installation and configuration is [explained here](./doc/mosquitto.md).

### Docker Containers
t.b.d.

