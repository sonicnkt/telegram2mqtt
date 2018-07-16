# -*- Dockerfile -*-

FROM python:2.7.15-slim-jessie
RUN pip install paho-mqtt python-telegram-bot pyyaml
RUN mkdir -p /opt/tel2mqtt/conf
COPY telegram2mqtt.py /opt/tel2mqtt
CMD ["python", "/opt/tel2mqtt/telegram2mqtt.py"]
