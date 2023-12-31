# Multiplus Power Control
Call stack: *multiplus_control.py -> ctrl_mp.py (MpControllMultiplusModbus())*

The script receives the measurement values provided by 
- Victron's Multiplus II
- EM24
- Victron MPPT charger
- House solar charger (derived values)
- Tibber / Tibber Pulse
- current battery SOC
  '

Based on these measurement data, the recalculation of the *Victron Multiplus II* power value is triggered.
```
self.controllerMultiplus.recalc(
    self.TibberPower - self.TibberProduction,
    self.EM24Power,
    self.VictronMpPower,
    self.Soc,
    self.VictronPvProduction,
)
```
This will control the power mode (inverter or charger) of the *Victron Multiplus II*, based on the given limits ([see config.ini](/src/config/config.ini)).

## Docker Container Creation
The docker image is created locally for the Raspberry architecture, transmitted to Dockerhub, and pulled by the Raspberry PI.
We are starting at the parent directory.

May be you must delete any further installations
```
docker stop multiplus_control 
docker rm multiplus_control
docker rmi multiplus_control:v1
```

The docker container can be investigated by
`docker exec -it multiplus_control /bin/bash`

Two docker files are provided: Dockerfile and Dockerfile_Raspi.

The first is for local builds.
 ```
 docker build -f ./docker/multiplus_control/Dockerfile -t "multiplus_control:v1" .
 docker run -it --name multiplus_control --env MQTT_USER=mqtt-user --env MQTT_PWD=SbzDdr88 multiplus_control:v1
 ```

The second docker file is for your Raspberry Pi: locally build and published on Docker Hub
It requires you are logged in on Docker Hub
```
docker login
```
The docker image is created and pushed on Docker Hub
```
docker buildx build -f ./docker/multiplus_control/Dockerfile_Raspi --platform linux/arm64,linux/arm/v7 -t "avenqo/multiplus_control:v1" --push .
```

On Raspberry Pi, you may pull the new created docker image.
```
docker run -it --name multiplus_control --restart always --env MQTT_USER=mqtt-user --env MQTT_PWD=SbzDdr88 avenqo/multiplus_control:v1
```
