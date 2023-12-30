FROM python:3.11.7-alpine3.19

WORKDIR /tibber_pulse
COPY ./ /tibber_pulse/
RUN pip install -U pip
RUN pip install -U paho-mqtt==1.6.1
RUN pip install requests
RUN pip install gql
RUN pip install websockets
RUN pip install parse
RUN pip3 install python-dateutil

WORKDIR /tibber_pulse/src/
CMD ./tibber_respawn.sh