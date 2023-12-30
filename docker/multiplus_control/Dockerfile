FROM python:3.11.7-alpine3.19
WORKDIR /multiplus_control
COPY ./ /multiplus_control/
RUN pip install -U pip
RUN pip install -U pymodbus==3.6.2
RUN pip install -U paho-mqtt==1.6.1
# Trigger Python script
WORKDIR /multiplus_control/src/
CMD ["python3", "multiplus_control.py"]
