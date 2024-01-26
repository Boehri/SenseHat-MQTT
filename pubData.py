#Standardbibliotheken
import time
import json
import os    

# Drittanbieterbibliotheken
import paho.mqtt.client as mqtt
from sense_hat import SenseHat

# Erstellen eines SenseHat-Objekts zur Interaktion mit dem Sense Hat
sense = SenseHat()

# Konfigurationsdaten für den HiveMQ Cloud MQTT Broker
broker_address = "5d4607be694c4b98bdfdab8fd5f11847.s2.eu.hivemq.cloud"  # Broker-Adresse
port = 8883  # Port für MQTT
username = "raspi_pub"  # Benutzername für die Authentifizierung
password = "Raspi_pub1"  # Passwort für die Authentifizierung

# Erstellen eines MQTT Client-Objekts mit einem eindeutigen Namen
client = mqtt.Client("Raspi_outside")
client.username_pw_set(username, password)  # Setzen der Authentifizierungsdetails

# Aktivieren der SSL/TLS Einstellungen für eine sichere Kommunikation
client.tls_set()

# Funktion zum Auslesen der CPU-Temperatur des Raspberry
def get_cpu_temp():
    res = os.popen("vcgencmd measure_temp").readline()
    return float(res.replace("temp=", "").replace("'C\n", ""))

# Funktion zur Korrektur der gemessenen Temperatur, basierend auf der CPU-Temperatur
def get_corrected_temp(raw_temp):
    cpu_temp = get_cpu_temp()
    # Anpassungsfaktor für die Temperaturkorrektur
    corrected_temp = raw_temp - ((cpu_temp - raw_temp) / 2.9)
    return corrected_temp

# Callback-Funktion, die aufgerufen wird, wenn eine Verbindung zum MQTT-Broker hergestellt wird
def on_connect(client, userdata, flags, rc):
    print("Verbunden mit dem MQTT Broker mit dem Code: " + str(rc))

# Zuweisen der Callback-Funktion zum MQTT-Client
client.on_connect = on_connect

# Herstellen der Verbindung zum MQTT-Broker
client.connect(broker_address, port)

# Starten des MQTT-Clients im Hintergrund
client.loop_start()

# Hauptprogrammschleife
try:
    while True:
        # Auslesen der Sensordaten vom Sense Hat
        raw_temp = sense.get_temperature()  # Rohwert der Temperatur
        corrected_temp = get_corrected_temp(raw_temp)  # Korrigierter Temperaturwert
        humidity = sense.get_humidity()  # Luftfeuchtigkeit
        pressure = sense.get_pressure()  # Luftdruck

        # Umwandlung der Sensordaten in JSON-Format zur Übertragung
        temp_data = json.dumps({'temperature': round(corrected_temp, 2)})
        humi_data = json.dumps({'humidity': round(humidity, 2)})
        press_data = json.dumps({'pressure': round(pressure, 2)})

        # Senden der Sensordaten an den MQTT-Broker
        client.publish("raspi/out/temp", temp_data)
        client.publish("raspi/out/humi", humi_data)
        client.publish("raspi/out/press", press_data)

        # Warte 10 Sekunden vor der nächsten Messung
        time.sleep(10)

# Beenden des Programms bei Unterbrechung (z.B. durch Drücken von Ctrl+C)
except KeyboardInterrupt:
    print("Programm wird beendet")
    client.loop_stop()  # Beenden des MQTT-Client-Loops
    client.disconnect()  # Trennen der Verbindung zum MQTT-Broker
