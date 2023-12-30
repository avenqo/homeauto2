#!/bin/sh
# Start Tibber Publisher
while true
do
python3 tibber_pulse_pub.py
echo "'tibber_pulse_pub.py' crashed with exit code $?.  Respawning.." >&2
sleep 10
done

