import paho.mqtt.client as mqtt
from sense_hat import SenseHat
import time
import json
import os

# Initialisiere SenseHat
sense = SenseHat()

# HiveMQ Cloud Broker Einstellungen
broker = "5d4607be694c4b98bdfdab8fd5f11847.s2.eu.hivemq.cloud"
port = 8883
username = "raspi_pub" 
password = "Raspi_pub1"

# Erstellen des MQTT Clients
client = mqtt.Client()
client.username_pw_set(username, password)

# SSL/TLS Einstellungen aktivieren
client.tls_set()

# Funktion zum Auslesen der CPU-Temperatur
def get_cpu_temp():
    res = os.popen("vcgencmd measure_temp").readline()
    return float(res.replace("temp=", "").replace("'C\n", ""))

# Funktion zur Berechnung der korrigierten Temperatur
def get_corrected_temp(raw_temp):
    cpu_temp = get_cpu_temp()
    corrected_temp = raw_temp - ((cpu_temp - raw_temp) / 1.5)
    return corrected_temp

def get_corrected_humi(raw_humi): 
    corrected_humi = raw_humi + 10
    return corrected_humi

# Callback, wenn eine Verbindung zum Broker hergestellt wurde
def on_connect(client, userdata, flags, rc):
    print("Verbunden mit dem MQTT Broker mit dem Code: " + str(rc))

# Callback Funktionen zuweisen
client.on_connect = on_connect
# Verbindung zum Broker herstellen
client.connect(broker, port)

# Starte den Loop im Hintergrund
client.loop_start()

# Hauptprogrammschleife
try:
    while True:
        # Messungen von SenseHat
        raw_temp = sense.get_temperature()
        corrected_temp = get_corrected_temp(raw_temp)
        raw_humi = sense.get_humidity()
        corrected_humi = get_corrected_humi(raw_humi)
        pressure = sense.get_pressure()

        # JSON Daten für MQTT
        temp_data = json.dumps({'temperature': round(corrected_temp, 2)})
        humi_data = json.dumps({'humidity': round(corrected_humi, 2)})
        press_data = json.dumps({'pressure': round(pressure, 2)})

        # Daten an MQTT Broker senden
        client.publish("raspi/in/temp", temp_data)
        client.publish("raspi/in/humi", humi_data)
        client.publish("raspi/in/press", press_data)

        time.sleep(10)
except KeyboardInterrupt:
    print("Programm wird beendet")
    client.loop_stop()
    client.disconnect()

