#!/bin/bash
# Start Tibber Publisher
export MQTT_USER=mqtt-user
export MQTT_PWD=SbzDdr88


while true
do
    python3 victron_publisher.py
    echo "'victron_publisher' crashed with exit code $?.  Respawning after a few seconds ..." >&2
    sleep 10
done
