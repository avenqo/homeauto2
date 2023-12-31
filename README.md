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
### Energy Measurements
![measurements](./doc/drawings//energy_calculation.png).

## Preconditions
### Docker
The docker container must be created locally. Therefore, docker must be installed on
- on your target system (Raspberry Pi)
- on your host for building the docker images (for docker image creation purposes only)

## Components
The system consists of 4 socker containers running on Raspberry Pi 3b+.
### Mosquitto (MQTT Server)
The MQTT server is the information broker in the middle of the system.
Installation and configuration is [explained here](./doc/mosquitto.md).

### Multiplus (Power) Control
Takes the values from MQTT Broker and recalculates the power flow for Victron Multiplus  meaning inverter or charger mode, depending on power balance. 
[read more](./doc/multiplus_control.md)

### Victron Publisher
Reads the value from Victron Multiplus, Victron MPPT charger and EM24 and publish them on MQTT Broker.
[read more](./doc/victron_publisher.md)

### Tibber Publisher
- Opens a websockert connection via [Tibber API](https://developer.tibber.com/docs/guides/calling-api)
- receives the power consumption and production values
- publishes the values on MQTT Broker.
[read more](./doc/tibber_publisher.md)



