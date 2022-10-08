# -*- Dockerfile -*-
FROM python:3-alpine
RUN apk add ffmpeg
# RUN pip install --upgrade pip
RUN pip install queuelib paho-mqtt python-telegram-bot pyyaml pydub
RUN mkdir -p /opt/tel2mqtt/conf mkdir -p /opt/tel2mqtt/sample
#RUN rm -rf /var/lib/apt/lists/*
COPY telegram2mqtt.py /opt/tel2mqtt
COPY config.yaml /opt/tel2mqtt/sample

VOLUME /opt/tel2mqtt/conf
CMD ["python", "/opt/tel2mqtt/telegram2mqtt.py"]
