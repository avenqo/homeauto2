# Python Base Image from https://hub.docker.com/r/arm32v7/python/
FROM python:3.11.7-alpine3.19

WORKDIR /victron_publisher
COPY ./ /victron_publisher/

RUN pip install -U pip
RUN pip install -U pymodbus==3.6.2
RUN pip install -U paho-mqtt==1.6.1
# Trigger Python script
WORKDIR /victron_publisher/src/
CMD ["python3", "victron_publisher.py"]
