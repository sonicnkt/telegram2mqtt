# -*- coding: utf-8 -*-
#################################################
## Telegram Audio/Voice 2 MQTT/Home Assistant  ##
#################################################
import logging, time, sys, yaml, os, traceback

from pydub import AudioSegment
from encodings import utf_8
from telegram import ForceReply, Update
from telegram.ext import CallbackContext, Updater, CommandHandler, MessageHandler, Filters
# , ContextTypes, , 
import paho.mqtt.client as mqtt
from threading import Thread
# import queue as Queue
try:
    from queue import Queue # using Python 3
    # from queue import * # using Python 3
except ImportError:
    from Queue import Queue   # falls back to import from Python 2
try:
    import http.server as SimpleHTTPServer # using Python 3
except ImportError:
    import SimpleHTTPServer   # falls back to import from Python 2
try:
    import socketserver as SocketServer # using Python 3
except ImportError:
    import SocketServer   # falls back to import from Python 2


# Change Working directory to Script directory
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)


# Callback for an established MQTT broker connection
def mqtt_on_connect(broker, userdata, flags, rc):
    logging.info("MQTT: Connected with the broker...")
def mqtt_on_disconnect(broker, userdata, rc):
    logging.info("MQTT: DISCONNECTED !!!!!!!!!!!!!!!!!!")
def mqtt_on_message(client, obj, msg):
    logging.info("Message: " + msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
def mqtt_on_publish(client, obj, mid):
    logging.debug("mid: " + str(mid))
def mqtt_on_subscribe(client, obj, mid, granted_qos):
    logging.debug("Subscribed: " + str(mid) + " " + str(granted_qos))
def mqtt_on_log(client, obj, level, string):
    logging.debug("Printed: " + string)

# MQTT Publisher Thread
class MQTTPublisher(object):
    def __init__(self, myqueue):
        self.myqueue = myqueue
        thread3 = Thread(target=self.run, args=())
        thread3.daemon = True  # Daemonize thread
        thread3.start()  # Start the execution

    def run(self):
        while True:
            if not self.myqueue.empty():
                payload = self.myqueue.get()
                # Adding "New" Flag to payload!
                payload["new"] = "true"
                # reformatting payload dict to str
                str_payload = repr(payload).replace("\'", "\"").replace("u\"", "\"")
                logging.info("--- Publishing MQTT Message ---")
                logging.info("Payload: " + str_payload)
                broker.publish(cfg["mqtt"]["topic"], payload=str_payload, qos=0, retain=True)
                time.sleep(payload["duration"] + 1.5)
                logging.info("--- Publishing MQTT Reset Payload ---")
                broker.publish(cfg["mqtt"]["topic"], payload="{\"new\": \"false\"}", qos=0, retain=True)
                time.sleep(0.5)
            else:
                time.sleep(0.2)

# Simple HTTP Server
class HttpServer(object):
    def __init__(self, port=8000):
        self.port = port
        thread1 = Thread(target=self.run, args=())
        thread1.daemon = True  # Daemonize thread
        thread1.start()  # Start the execution

    def run(self):
        Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
        Handler.extensions_map.update({
            '.webapp': 'application/x-web-app-manifest+json',
        })
        self.httpd = SocketServer.TCPServer(("", self.port), Handler)
        self.httpd.serve_forever()

    def stop(self):
        self.httpd.shutdown()

# Telegram Bot
class TelegramBot(object):
    def __init__(self, token, queue, web_port, web_domain):
        self.token = token
        self.myqueue = queue
        self.web_port = web_port
        self.web_name = web_domain
        thread2 = Thread(target=self.run, args=())
        thread2.daemon = True  # Daemonize thread
        thread2.start()  # Start the execution

    def start(self, update: Update, context: CallbackContext):
        """Send a message when the command /start is issued."""
        context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

    def text(self, update: Update, context: CallbackContext):
        # Add User ID translation
        user_id = update.message.from_user.id
        self.myqueue.put({"type" : "text",
                          "user" : str(user_id),
                          "content" : update.message.text,
                          "duration" : 0})

    def voice(self, update: Update, context: CallbackContext):
        user_id = update.message.from_user.id
        if cfg["allowed_contacts"] and (user_id in cfg["allowed_contacts"].keys()):
            username = cfg["allowed_contacts"][user_id]
            # Downloading Voice
            newfile = context.bot.get_file(update.message.voice.file_id)
            str_filename = time.strftime("%Y-%m-%d_%H-%M") + '_' + str(user_id) 
            input_file = str_filename + '.ogg'
            output_file = str_filename + '.mp3'
            newfile.download(input_file)
            sound = AudioSegment.from_ogg(input_file)
            sound.export(output_file, format="mp3")
            fileurl = "http://" + self.web_name + ":{}/".format(str(self.web_port)) + output_file
            self.myqueue.put({"type": "voice",
                              "user": username,
                              "content": fileurl,
                              "duration": int(update.message.voice.duration)})
        else:
            logging.info("Voice Message rejected from user_id: {}".format(user_id))

    def run(self):
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
        self.updater = Updater(token=self.token)
        self.dispatcher = self.updater.dispatcher

        # Handler Define

        start_handler = CommandHandler('start', self.start)
        log_handler   = MessageHandler(Filters.text, self.text)
        voice_handler = MessageHandler(Filters.voice, self.voice)

        # Handler Registry
        self.dispatcher.add_handler(start_handler)
        self.dispatcher.add_handler(log_handler)
        self.dispatcher.add_handler(voice_handler)

        # Start Main Routine
        self.updater.start_polling()

    def shutdown(self):
        self.updater.stop()

def main(argv):
    # ADD gobals: other background tasks, contacts dict
    global broker
    global cfg

    # Config Parser
    try:
        f = open('conf/config.yaml', 'r', encoding="utf_8")
        # f = open('config.yaml', 'r', encoding="utf_8")
    except IOError:
        print("Can't open config file!")
        sys.exit(1)
    else:
        with f:
            cfg = yaml.full_load(f) 
    #with open("conf/config.yaml", 'r') as ymlfile:
    #    cfg = yaml.load(ymlfile)


    log_level = logging.INFO  # Deault logging level
    if cfg["other"]["loglevel"] == 1:
        log_level = logging.ERROR
    elif cfg["other"]["loglevel"] == 2:
        log_level = logging.WARN
    elif cfg["other"]["loglevel"] == 3:
        log_level = logging.INFO
    elif cfg["other"]["loglevel"] >= 4:
        log_level = logging.DEBUG

    root = logging.getLogger()
    root.setLevel(log_level)
    # A more docker-friendly approach is to output to stdout
    logging.basicConfig(stream=sys.stdout, format="%(asctime)s - %(levelname)s - %(message)s",
                        datefmt="%m/%d/%Y %I:%M:%S %p", level=log_level)

    # Log startup messages and our configuration parameters
    logging.info("------------------------")
    logging.info("Starting up...")
    logging.info("--- MQTT Broker Configuration ---")
    logging.info("Domain: " + cfg["mqtt"]["domain"])
    logging.info("Port: " + str(cfg["mqtt"]["port"]))
    logging.info("Protocol: " + cfg["mqtt"]["protocol"])
    logging.info("Username: " + cfg["mqtt"]["username"])
    logging.info("Keepalive Interval: " + str(cfg["mqtt"]["keepalive"]))
    logging.info("Status Topic: " + cfg["mqtt"]["topic"])
    logging.info("--- Webserver Configuration ---")
    logging.info("Domain: " + cfg["webserver"]["domain"])
    logging.info("Port: " + str(cfg["webserver"]["port"]))
    logging.info("--- Telegram Configuration ---")
    logging.info("API Token: " + cfg["telegram"]["api-token"])


    try:
        ## Handle mqtt connection and callbacks
        #broker = mqtt.Client(client_id="", clean_session=True, userdata=None, protocol=eval("mqtt." + cfg["mqtt"]["protocol"]))
        #broker.username_pw_set(cfg["mqtt"]["username"], password=cfg["mqtt"]["password"])
        #broker.on_connect = mqtt_connect
        ##broker.on_message = mqtt_message #Callback for Message Receiving, not used atm
        #broker.connect(cfg["mqtt"]["domain"], cfg["mqtt"]["port"], cfg["mqtt"]["keepalive"])

        broker = mqtt.Client( protocol=eval("mqtt." + cfg["mqtt"]["protocol"]))
        broker.reinitialise(client_id="", clean_session=True, userdata=None)

        # Assign event callbacks
        broker.on_message = mqtt_on_message
        broker.on_connect = mqtt_on_connect
        broker.on_disconnect = mqtt_on_disconnect
        broker.on_publish = mqtt_on_publish
        broker.on_subscribe = mqtt_on_subscribe
        # broker.on_log = on_log
        broker.username_pw_set(cfg["mqtt"]["username"], cfg["mqtt"]["password"])
        broker.connect(cfg["mqtt"]["domain"], cfg["mqtt"]["port"],cfg["mqtt"]["keepalive"])


        myqueue = Queue()

        #Creating and changing to downloader/webserver directory
        workdir = "conf/web/"
        if not os.path.exists(workdir):
            os.makedirs(workdir)
        os.chdir(workdir)

        # Start Webserver Thread
        myweb = HttpServer(port=cfg["webserver"]["port"])
        # Start Telegram Bot Thread
        bot = TelegramBot(cfg["telegram"]["api-token"], myqueue, cfg["webserver"]["port"], cfg["webserver"]["domain"])
        #Start Publisher Thread
        publish = MQTTPublisher(myqueue)

    except Exception as e:
        logging.critical("Exception: " + str(e))
        sys.exit(1)

    # Main work loop
    try:
        rc = broker.loop_start()
        if rc:
            logging.warn("Warning: " + str(rc))
        while True:
            time.sleep(1)
        broker.loop_stop()
    except Exception as e:
        logging.critical("Exception: " + str(e))
        sys.exit(1)


# Get things started
if __name__ == '__main__':
    main(sys.argv[1:])