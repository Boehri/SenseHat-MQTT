import paho.mqtt.client as mqtt
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import json
import threading
import time

# HiveMQ Cloud Broker Einstellungen
broker = "5d4607be694c4b98bdfdab8fd5f11847.s2.eu.hivemq.cloud"
port = 8883
username = "" # Ersetzen durch Benutzernamen
password = ""  # Ersetzen durch Passwort

# MongoDB Atlas Verbindungsdetails
uri = ""  # Ersetzen durch MongoDB ID
database_name = ""  # Name der Datenbank
collection_name = ""  # Name der Sammlung (Collection)

# Erstellen eines neuen MongoClient und aufbauen der Verbindung mit dem Server
mongo_client = MongoClient(uri, server_api=ServerApi('1'))
db = mongo_client[database_name]
collection = db[collection_name]

# Überprüfen Sie die Verbindung
try:
    mongo_client.admin.command('ping')
    print("Erfolgreich mit MongoDB verbunden!")
except Exception as e:
    print(f"MongoDB Verbindungsfehler: {e}")
    exit()

# Datenzwischenspeicher
data_cache = {
    "temperature": None,
    "humidity": None,
    "pressure": None,
    "feelsLike": None
}
# Funktion, um Daten in die Datenbank zu schreiben
def write_to_db():
    while True:
        time.sleep(60) 
        current_time = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        data_to_insert = {
            "timestamp": current_time,
            "temperature": data_cache["temperature"],
            "humidity": data_cache["humidity"],
            "pressure": data_cache["pressure"],
            "feelsLike": data_cache["feelsLike"],
        }
        collection.insert_one(data_to_insert)
        print(f"Daten geschrieben: {data_to_insert}")

# Erstellen des MQTT Clients
mqtt_client = mqtt.Client()
mqtt_client.username_pw_set(username, password)
mqtt_client.tls_set()  # SSL/TLS Einstellungen aktivieren

# MQTT Callback-Funktionen
def on_connect(client, userdata, flags, rc):
    print("Verbunden mit dem MQTT Broker mit dem Code: " + str(rc))
    client.subscribe("raspi/in/temp")
    client.subscribe("raspi/in/humi")
    client.subscribe("raspi/in/press")
    client.subscribe("raspi/in/temp/feelsLike")
    
#Schreiben der empfangenen Daten in den Cache
def on_message(client, userdata, msg):
    print(f"Nachricht erhalten: {msg.topic} {str(msg.payload)}")
    try:
        payload = json.loads(msg.payload)
        if msg.topic == "raspi/in/temp":
            data_cache["temperature"] = payload.get("temperature")
        elif msg.topic == "raspi/in/humi":
            data_cache["humidity"] = payload.get("humidity")
        elif msg.topic == "raspi/in/press":
            data_cache["pressure"] = payload.get("pressure")
        elif msg.topic == "raspi/temp/feelsLike":
            data_cache["feelsLike"] = payload.get("feelsLike")
    except Exception as e:
        print(f"Fehler beim Verarbeiten der Nachricht: {e}")


# Callback Funktionen zuweisen
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

# Verbindung zum Broker herstellen
mqtt_client.connect(broker, port)

# Starte den Loop im Hintergrund
mqtt_client.loop_start()

# Starte den Datenbankschreib-Thread
db_thread = threading.Thread(target=write_to_db)
db_thread.start()

try:
    while True:
        pass  # Haupt-Loop des Skripts
except KeyboardInterrupt:
    print("Programm wird beendet")
    mqtt_client.loop_stop()
    mqtt_client.disconnect()
    db_thread.join()  # Warten auf das Ende des Datenbankschreib-Threads

