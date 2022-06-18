# -*- Dockerfile -*-

FROM python:slim
#RUN apt-get update && apt-get upgrade -y && apt-get install -y python3-pip
RUN pip install paho-mqtt python-telegram-bot pyyaml
RUN mkdir -p /opt/tel2mqtt/conf
COPY telegram2mqtt.py /opt/tel2mqtt
COPY config.yaml /opt/tel2mqtt/conf
RUN rm -rf /var/lib/apt/lists/*
CMD ["python", "/opt/tel2mqtt/telegram2mqtt.py"]

