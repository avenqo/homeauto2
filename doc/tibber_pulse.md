# Tibber Pulse - Reading and publishing
## Goal
The idea of the module is to subscribe to Tibber and listening for power values published by Tibber via Websockets.
[Some more informations on Tibber](https://developer.tibber.com/docs/guides/calling-api)

The read values are taken and published to a MQTT broker

## Published messages

/home/tibber/pulse/power/current/consumption
/home/tibber/pulse/power/current/production
