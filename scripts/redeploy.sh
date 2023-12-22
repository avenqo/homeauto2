#!/bin/bash
# Redeploy configured mosquitto container
# stop container
docker stop mosquitto || true
#cleanup
docker rm mosquitto || true
docker rmi eclipse-mosquitto || true
#reinstall and start
cd ./docker/mosquitto
docker compose up -d
cd ../../