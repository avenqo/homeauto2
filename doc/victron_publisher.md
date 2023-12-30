# Victron Publisher
victron_publisher.sh -> victron_publisher.py -> MpModbus()

The script reads out the measurement values provided by Victron's Multiplus II; these values are published on MQTT Server.
'''   
mqttPublisher.publish(MQTT_TOPIC_EM24_CONSUMPTION, EM24Power)
mqttPublisher.publish(MQTT_TOPIC_MP_POWER, VictronMpPower)
mqttPublisher.publish(MQTT_TOPIC_MP_SOC, Soc)
mqttPublisher.publish(MQTT_TOPIC_MPPT_SOLAR_POWER, VictronPvPower)
'''
## Docker Container Creation
The Docker file is created locally for the Raspberry architecture, transmitted to Dockerhub, and pulled by the Raspberry PI.
We are starting at the parent directory.

May be you must delete any further installations
```
docker stop victron_publisher 
docker rm victron_publisher
docker rmi victron_publisher:v1
```

The Docker container can be investigated by
`docker exec -it victron_publisher /bin/bash`

Two Dockerfiles are provided: Dockerfile and Dockerfile_Raspi.

The first is for local builds.
 `docker build -f ./docker/victron_publisher/Dockerfile -t "victron_publisher:v1" .`
 `docker run -it --name victron_publisher --env MQTT_USER=mqtt-user --env MQTT_PWD=SbzDdr88 victron_publisher:v1`

The second Dockerfile is for your Raspberry Pi: locally build and published on Dockerhub
It requires you are logged in on Dockerhub
`docker login`
The Docker image is created and pushed on Dockerhub
`docker buildx build -f ./docker/victron_publisher/Dockerfile_Raspi --platform linux/arm64,linux/arm/v7 -t "avenqo/victron_publisher:v1" --push .`

On Raspberry Pi, you may pull the new created image.
`docker run -it --name victron_ctrl --restart always --env MQTT_USER=mqtt-user --env MQTT_PWD=SbzDdr88 avenqo/victron_publisher:v1`


