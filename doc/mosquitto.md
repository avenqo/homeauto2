# Mosquitto Docker Container

The MQTT Message Broker consumes and provides all data being necessary to control the power flow from and to the grid and LiFePo battery. This includes measurement and configuration data like:
- Victron Multiplus
- Victron MPPT
- EM24
- Tibber Pulse
- Configuration data

## Create Image & first Run
```
cd homeauto2/docker/mosquitto
docker compose up -d
```
The container is now up and running named as **mosquitto**.

## Credentials
The default credentials (user, password) are `mqtt-user` and password is `SbzDdr88`.
If you change the password then change it for the other docker containers accordingly.

The credentials may be changed via an interactive terminal session with the running mosquitto container.
```
docker exec -it mosquitto sh
    mosquitto_passwd -c /mosquitto/data/pwfile mqtt-user
    Password: secret
    exit
```
> Question: Is a container restart sufficient?

## Useful commands
### Interactive terminal
Open a interactive shell
```
docker exec -it mosquitto sh
```

### Run, stop, remove container & image
```
docker start mosquitto
docker stop mosquitto
docker rm mosquitto
docker rmi eclipse-mosquitto
```
