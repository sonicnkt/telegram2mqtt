# telegram2mqtt

telegram2mqtt is a small python program that is using the python telegram bot to download voice messages, hosting them through a simple webserver and sends informations regarding those messages to an mqtt server. 

In combination with something like Home Assistant you can automatically playback those messages at Home.

There is only support for normal text messages and voice recordings atm, but i will improve this in the future (i hope ;) )

In this repository you will also find a Dockerfile to build a compatible Container, the program requires a config.yaml to work correctly inside a conf folder, the downloaded voice files will be stored inside a web folder inside the conf directory.

```
  /opt/telegram2mqtt
  /opt/telegram2mqtt/telegram2mqtt.py
  /opt/telegram2mqtt/conf
  /opt/telegram2mqtt/conf/config.yaml
  /opt/telegram2mqtt/conf/web
```

If you are using docker map the config directory to a place outside of the container.


You can find a simple home assistant integration example here: https://github.com/sonicnkt/telegram2mqtt/blob/master/ha_config.yaml
