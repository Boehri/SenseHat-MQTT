# Standardbibliotheken
from datetime import datetime, timedelta  # Import für Datum- und Zeitfunktionen
import json  # Import zur Verarbeitung von JSON-Daten
import time  # Import für Zeitfunktionen wie Warten (sleep)

# Drittanbieterbibliotheken
from pymongo import MongoClient  # MongoDB Client-Bibliothek
import paho.mqtt.client as mqtt  # MQTT Client-Bibliothek

# Funktion zur Berechnung des Durchschnitts einer Liste von Werten
def calculate_average(values):
    return sum(values) / len(values) if values else 0

# Funktion zum Abrufen und Berechnen von Durchschnittswerten aus der MongoDB
def get_average_values(collection, start_date, end_date):

    # Erstellt eine MongoDB-Abfrage zwischen den angegebenen Daten
    query = {"timestamp": {"$gte": start_date.isoformat(), "$lt": end_date.isoformat()}}
    documents = collection.find(query)  # Führt die Abfrage aus

    # Extrahiert und berechnet die Durchschnittswerte für Temperatur, Feuchtigkeit und Druck
    temperatures = [doc["temperature"] for doc in documents if doc["temperature"] is not None]
    documents.rewind()
    humidities = [doc["humidity"] for doc in documents if doc["humidity"] is not None]
    documents.rewind()
    pressures = [doc["pressure"] for doc in documents if doc["pressure"] is not None]

    return calculate_average(temperatures), calculate_average(humidities), calculate_average(pressures)

# Verbindung zur Cloud MongoDB herstellen
cloud_mongo_uri = "mongodb+srv://MQTT_TEMP:MQTT_TEMP@tempdata.ky889by.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(cloud_mongo_uri)  # Erstellen einer MongoDB-Client-Instanz
db = client["TempData"]  # Auswahl der Datenbank
collection = db["TimestampData"]  # Auswahl der Collection

# HiveMQ Cloud Broker Einstellungen
broker = "5d4607be694c4b98bdfdab8fd5f11847.s2.eu.hivemq.cloud"  # MQTT Broker Adresse
port = 8883  # Port für MQTT über SSL/TLS
username = "raspi_pub"  # MQTT Benutzername
password = "Raspi_pub1"   # MQTT Passwort

# Erstellen des MQTT Clients
client = mqtt.Client("AverageDataClient")  # Erstellen einer MQTT-Client-Instanz
client.username_pw_set(username, password)  # Setzen von Benutzername und Passwort

# SSL/TLS Einstellungen aktivieren
client.tls_set()  # Aktivieren von SSL/TLS für sichere Kommunikation

# Callback, wenn eine Verbindung zum Broker hergestellt wurde
def on_connect(client, userdata, flags, rc):
    print("Verbunden mit dem MQTT Broker mit dem Code: " + str(rc))

# Callback Funktionen zuweisen
client.on_connect = on_connect  # Zuweisung der Callback-Funktion

# Verbindung zum Broker herstellen
client.connect(broker, port)  # Verbinden mit dem MQTT Broker

# Starte den MQTT-Client-Loop im Hintergrund
client.loop_start()

# Hauptprogrammschleife
try:
   while True:
    # Datumsgrenzen für die Datenabfrage festlegen
    start_date = datetime.now() - timedelta(days=7)  # Startdatum ist vor 7 Tagen
    end_date = datetime.now()  # Enddatum ist jetzt

    # Durchschnittswerte aus der Datenbank berechnen
    avg_temp, avg_humi, avg_press = get_average_values(collection, start_date, end_date)

    # JSON-Daten für die Übertragung vorbereiten
    temp_data = json.dumps({'avgTemperature': round(avg_temp, 2)})
    humi_data = json.dumps({'avgHumidity': round(avg_humi, 2)})
    press_data = json.dumps({'avgPressure': round(avg_press, 2)})

    # Daten an HiveMQ senden
    client.publish("raspi/in/temp/avg", temp_data)
    client.publish("raspi/in/humi/avg", humi_data)
    client.publish("raspi/in/press/avg", press_data)

    # 60 Sekunden warten vor dem nächsten Durchlauf
    time.sleep(60)

# Programm beenden, wenn ein Keyboard-Interrupt (CTRL+C) erfolgt
except KeyboardInterrupt:
    print("Programm wird beendet")
    client.loop_stop()  # Stoppen des MQTT-Client-Loops
    client.disconnect()  # Trennen der Verbindung zum MQTT-Broker
