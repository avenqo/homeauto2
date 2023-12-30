# Multiplus Power Control
multiplus_control.py -> ctrl_mp.py (MpControllMultiplusModbus())

The script receives the measurement values provided by Victron's Multiplus II; 
'''   
mqttPublisher.publish(MQTT_TOPIC_EM24_CONSUMPTION, EM24Power)
mqttPublisher.publish(MQTT_TOPIC_MP_POWER, VictronMpPower)
mqttPublisher.publish(MQTT_TOPIC_MP_SOC, Soc)
mqttPublisher.publish(MQTT_TOPIC_MPPT_SOLAR_POWER, VictronPvPower)
'''

Based on this, the recalculation of the power value is triggered.
```
self.controllerMultiplus.recalc(
    self.TibberPower - self.TibberProduction,
    self.EM24Power,
    self.VictronMpPower,
    self.Soc,
    self.VictronPvProduction,
)
```


## Docker Container Creation
The Docker file is created locally for the Raspberry architecture, transmitted to Dockerhub, and pulled by the Raspberry PI.
We are starting at the parent directory.

May be you must delete any further installations
```
docker stop multiplus_control 
docker rm multiplus_control
docker rmi multiplus_control:v1
```

The Docker container can be investigated by
`docker exec -it multiplus_control /bin/bash`

Two Dockerfiles are provided: Dockerfile and Dockerfile_Raspi.

The first is for local builds.
 `docker build -f ./docker/multiplus_control/Dockerfile -t "multiplus_control:v1" .`
 `docker run -it --name multiplus_control --env MQTT_USER=mqtt-user --env MQTT_PWD=SbzDdr88 multiplus_control:v1`

The second Dockerfile is for your Raspberry Pi: locally build and published on Dockerhub
It requires you are logged in on Dockerhub
`docker login`
The Docker image is created and pushed on Dockerhub
`docker buildx build -f ./docker/multiplus_control/Dockerfile_Raspi --platform linux/arm64,linux/arm/v7 -t "avenqo/multiplus_control:v1" --push .`

On Raspberry Pi, you may pull the new created image.
`docker run -it --name multiplus_control --restart always --env MQTT_USER=mqtt-user --env MQTT_PWD=SbzDdr88 avenqo/multiplus_control:v1`


