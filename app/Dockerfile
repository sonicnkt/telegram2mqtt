# -*- Dockerfile -*-

FROM python:3-alpine
RUN apk add ffmpeg
RUN pip install queuelib paho-mqtt python-telegram-bot pyyaml pydub
RUN mkdir -p /opt/tel2mqtt/conf
#RUN rm -rf /var/lib/apt/lists/*
COPY telegram2mqtt.py /opt/tel2mqtt
VOLUME /opt/tel2mqtt/conf
CMD ["python", "/opt/tel2mqtt/telegram2mqtt.py"]