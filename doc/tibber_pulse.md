# Tibber Pulse - Reading and publishing
## Goal
The idea of the module is to subscribe to Tibber and listening for power values published by Tibber via Websockets.
[Some more informations on Tibber](https://developer.tibber.com/docs/guides/calling-api)

The read values are taken and published to a MQTT broker

## Docker Container Creation
The Docker file is created locally for the Raspberry architecture, transmitted to Dockerhub, and pulled by the Raspberry PI.
We are starting at the parent directory.

May be you must delete any further installations
```
docker stop tibber_publisher 
docker rm tibber_publisher
docker rmi tibber_publisher:v1
```

The Docker container can be investigated by
`docker exec -it tibber_publisher /bin/bash`

Two Dockerfiles are provided: Dockerfile and Dockerfile_Raspi.

The first is for local builds.
 `docker build -f ./docker/tibber_publisher/Dockerfile -t "tibber_publisher:v1" .`
 `docker run -it --name tibber_publisher --env MQTT_USER=mqtt-user --env MQTT_PWD=SbzDdr88 --env TIBBER_API_TOKEN=e408GnWKYJBG7oVRipyB4azSunATvt4IpHeh5jRBnxo tibber_publisher:v1`

The second Dockerfile is for your Raspberry Pi: locally build and published on Dockerhub
It requires you are logged in on Dockerhub
`docker login`
The Docker image is created and pushed on Dockerhub
`docker buildx build -f ./docker/tibber_publisher/Dockerfile_Raspi --platform linux/arm64,linux/arm/v7 -t "avenqo/tibber_publisher:v1" --push .`

On Raspberry Pi, you may pull the new created image.
`docker run -it --name tibber_publisher --restart always --env MQTT_USER=mqtt-user --env MQTT_PWD=SbzDdr88 --env TIBBER_API_TOKEN=e408GnWKYJBG7oVRipyB4azSunATvt4IpHeh5jRBnxo avenqo/tibber_publisher:v1`


## Issues
### websockets.exceptionsConnectionClosedError
 'lastMeterConsumption': 2186.9218}}
2023-12-25 12:35:30,190 - root - ERROR - Module [websockets.exceptionsConnectionClosedError], Args [(None, None, None)]
Finally: Client closed.

This may happen somtimes for any reason. Therefore, the tibber python publisher isn't started cirectly but supervised by an extra shell script trying to respawn the script in case of failures.

### Too many open connections ....
Sometimes, the connection may be reestablished after occurred exception, but it (sooner or later) always leads to a situation like this:
```
2023-12-25 08:49:54,547 - Rotating Multiplus Control - INFO - Connection was closed. Try to reconnecting ...
2023-12-25 08:50:00,553 - Rotating Multiplus Control - INFO - Tibber->fetch_data()
websockets.exceptionsConnectionClosedError
2023-12-25 08:50:06,027 - Rotating Multiplus Control - INFO - Connection was closed. Try to reconnecting ...
2023-12-25 08:50:12,032 - Rotating Multiplus Control - INFO - Tibber->fetch_data()
websockets.exceptionsConnectionClosedError
2023-12-25 08:50:12,394 - Rotating Multiplus Control - INFO - Connection was closed. Try to reconnecting ...
^CTraceback (most recent call last):
  File "/Users/hko/git/homeauto2/src/libs/pulse_reader.py", line 101, in fetch_data
    for result in ws_client.subscribe(subscription):
  File "/usr/local/lib/python3.9/site-packages/gql/client.py", line 600, in subscribe
    loop.run_until_complete(generator_task)
  File "/usr/local/Cellar/python@3.9/3.9.5/Frameworks/Python.framework/Versions/3.9/lib/python3.9/asyncio/base_events.py", line 642, in run_until_complete
    return future.result()
  File "/usr/local/lib/python3.9/site-packages/gql/client.py", line 586, in subscribe
    ] = loop.run_until_complete(
  File "/usr/local/Cellar/python@3.9/3.9.5/Frameworks/Python.framework/Versions/3.9/lib/python3.9/asyncio/base_events.py", line 642, in run_until_complete
    return future.result()
  File "/usr/local/lib/python3.9/site-packages/gql/client.py", line 470, in subscribe_async
    async with self as session:
  File "/usr/local/lib/python3.9/site-packages/gql/client.py", line 658, in __aenter__
    return await self.connect_async()
  File "/usr/local/lib/python3.9/site-packages/gql/client.py", line 632, in connect_async
    await self.transport.connect()
  File "/usr/local/lib/python3.9/site-packages/gql/transport/websockets_base.py", line 514, in connect
    raise e
  File "/usr/local/lib/python3.9/site-packages/gql/transport/websockets_base.py", line 512, in connect
    await self._initialize()
  File "/usr/local/lib/python3.9/site-packages/gql/transport/websockets.py", line 152, in _initialize
    await self._send_init_message_and_wait_ack()
  File "/usr/local/lib/python3.9/site-packages/gql/transport/websockets.py", line 149, in _send_init_message_and_wait_ack
    await asyncio.wait_for(self._wait_ack(), self.ack_timeout)
  File "/usr/local/Cellar/python@3.9/3.9.5/Frameworks/Python.framework/Versions/3.9/lib/python3.9/asyncio/tasks.py", line 481, in wait_for
    return fut.result()
  File "/usr/local/lib/python3.9/site-packages/gql/transport/websockets.py", line 124, in _wait_ack
    init_answer = await self._receive()
  File "/usr/local/lib/python3.9/site-packages/gql/transport/websockets_base.py", line 231, in _receive
    data: Data = await self.websocket.recv()
  File "/usr/local/lib/python3.9/site-packages/websockets/legacy/protocol.py", line 568, in recv
    await self.ensure_open()
  File "/usr/local/lib/python3.9/site-packages/websockets/legacy/protocol.py", line 953, in ensure_open
    raise self.connection_closed_exc()
websockets.exceptions.ConnectionClosedError: received 4429 (private use) Too many open connections on this server; count 2; user agent Python/3.9 websockets/10.4; then sent 4429 (private use) Too many open connections on this server; count 2; user agent Python/3.9 websockets/10.4
```
The only solution for it is to request a new API key and restart the docker container.