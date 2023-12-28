# Python Base Image from https://hub.docker.com/r/arm32v7/python/
FROM python:3.11.7-alpine3.19

WORKDIR /victron_publisher

COPY ./ /victron_publisher/

# Install python modules and pkill
RUN apk add procps
RUN apk add libxslt-dev libxml2-dev python3-dev
RUN apk add build-base
RUN pip install -U pip
# RUN pip3 install --upgrade pip
# RUN pip install -U pymodbus==3.0.2
RUN pip install -U pymodbus==3.6.2
RUN pip install -U paho-mqtt==1.6.1
# RUN pip install -U lxml==4.9.2

# RUN pip install requests-html==0.10.0

# Trigger Python script
WORKDIR /victron_publisher/src/
CMD ["python3", "victron_publisher.py"]
