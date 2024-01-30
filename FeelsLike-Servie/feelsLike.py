import paho.mqtt.client as mqtt
import json

# MQTT Einstellungen
broker = "" # Eingeben der Broker URL
port = 8883
username = "" # Eingeben des Benutzernamen
password = "" # Eingeben des Passworts

# Globale Variablen für die Sensordaten des ersten Sensors
temperature_in = None
humidity_in = None
temperature_in_updated = False
humidity_in_updated = False

# Globale Variablen für die Sensordaten des zweiten Sensors
temperature_out = None
humidity_out = None
temperature_out_updated = False
humidity_out_updated = False

# Funktion zur Berechnung der gefühlten Temperatur
def calculate_feels_like(temp, hum):
    if temp is None or hum is None:
        return None
    feels_like = temp - 0.55 * (1 - hum / 100) * (temp - 14.5)
    return round(feels_like, 2)

# Funktion, um die gefühlte Temperatur für den ersten Sensor zu veröffentlichen
def publish_feels_like_in(client):
    global temperature_in_updated, humidity_in_updated
    feels_like = calculate_feels_like(temperature_in, humidity_in)
    if feels_like is not None:
        client.publish("raspi/in/temp/feelsLike", json.dumps({"feelsLike": feels_like}))
        temperature_in_updated = False
        humidity_in_updated = False

# Funktion, um die gefühlte Temperatur für den zweiten Sensor zu veröffentlichen
def publish_feels_like_out(client):
    global temperature_out_updated, humidity_out_updated
    feels_like = calculate_feels_like(temperature_out, humidity_out)
    if feels_like is not None:
        client.publish("raspi/out/temp/feelsLike", json.dumps({"feelsLike": feels_like}))
        temperature_out_updated = False
        humidity_out_updated = False

# MQTT Callback - Wird aufgerufen, wenn eine Verbindung zum Broker hergestellt wird
def on_connect(client, userdata, flags, rc):
    client.subscribe("raspi/in/temp")
    client.subscribe("raspi/in/humi")
    client.subscribe("raspi/out/temp")
    client.subscribe("raspi/out/humi")

# MQTT Callback - Wird aufgerufen, wenn eine Nachricht empfangen wird
def on_message(client, userdata, msg):
    global temperature_in, humidity_in, temperature_in_updated, humidity_in_updated
    global temperature_out, humidity_out, temperature_out_updated, humidity_out_updated
    payload = json.loads(msg.payload.decode())

    if msg.topic == "raspi/in/temp":
        temperature_in = payload["temperature"]
        temperature_in_updated = True
    elif msg.topic == "raspi/in/humi":
        humidity_in = payload["humidity"]
        humidity_in_updated = True
    elif msg.topic == "raspi/out/temp":
        temperature_out = payload["temperature"]
        temperature_out_updated = True
    elif msg.topic == "raspi/out/humi":
        humidity_out = payload["humidity"]
        humidity_out_updated = True

    # Veröffentlichen für den ersten Sensor
    if temperature_in_updated and humidity_in_updated:
        publish_feels_like_in(client)
    
    # Veröffentlichen für den zweiten Sensor
    if temperature_out_updated and humidity_out_updated:
        publish_feels_like_out(client)

# MQTT Client-Setup
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.username_pw_set(username, password)
client.tls_set()  # Aktiviert TLS
client.connect(broker, port, 60)

# Startet den MQTT-Client
client.loop_forever()
