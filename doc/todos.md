# Todo's

## Docker: Control Loop
Control Loop should delegate Multiplus actions to victron publisher; therefore, docker container will not need pymodbus dependency anymore 

## Logging
how to change logging live
log level definition ->  config
different log files for different modules

## Config
config must be changeable during runtime!

## Delete

tibber_pulse

## Test
stop / restart MQTT Broker -> is reconnecting?

stop / restart publisher loops -> is power going idle? and controlled after restart?

## Rename 
mqtt_pub -> mqtt_client

## Other
Broker data -> get from config
    dito Username & pwd

MQTT Broker persistent?



Traceback (most recent call last):
  File "/Users/hko/git/homeauto2/src/ctrl_loop.py", line 48, in <module>
    mqttPublisher.client.loop_forever()
  File "/usr/local/lib/python3.9/site-packages/paho/mqtt/client.py", line 1756, in loop_forever
    rc = self._loop(timeout)
  File "/usr/local/lib/python3.9/site-packages/paho/mqtt/client.py", line 1164, in _loop
    rc = self.loop_read()
  File "/usr/local/lib/python3.9/site-packages/paho/mqtt/client.py", line 1558, in loop_read
    return self._loop_rc_handle(rc)
  File "/usr/local/lib/python3.9/site-packages/paho/mqtt/client.py", line 2350, in _loop_rc_handle
    self._do_on_disconnect(rc, properties)
  File "/usr/local/lib/python3.9/site-packages/paho/mqtt/client.py", line 3475, in _do_on_disconnect
    on_disconnect(self, self._userdata, rc)
TypeError: _on_disconnect() takes 3 positional arguments but 4 were given