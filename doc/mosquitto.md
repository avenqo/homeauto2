# Mosquitto Container

The MQTT Message Broker consumes and provides all data being necessary to control the power flow from and to the LiFePo battery.

The basics for docker container creation and configuration are coming from 
https://www.schaerens.ch/raspi-setting-up-mosquitto-mqtt-broker-on-raspberry-pi-docker/

## Clone
Update from git via:
`git clone git@github.com:avenqo/homeauto2.git`
or
`git pull origin`

## Create Image & first Run
```
cd homeauto2/docker/mosquitto
docker compose up -d
```

## Run, stop, remove container & image
```
docker start mosquitto
docker stop mosquitto
docker rm mosquitto
docker rmi eclipse-mosquitto
```

[Back to readme.md](../readme.md)

