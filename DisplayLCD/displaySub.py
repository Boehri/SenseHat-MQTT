# Standardbibliotheken
from datetime import datetime, timedelta  # Import für Datum- und Zeitfunktionen
import json  # Import zur Verarbeitung von JSON-Daten
import time  # Import für Zeitfunktionen wie Warten (sleep)

# Drittanbieterbibliotheke
import paho.mqtt.client as mqtt  # MQTT Client-Bibliothek
import pygame
from PIL import Image, ImageDraw, ImageFont

# HiveMQ Cloud Broker Einstellungen
broker = "5d4607be694c4b98bdfdab8fd5f11847.s2.eu.hivemq.cloud"  # MQTT Broker Adresse
port = 8883  # Port für MQTT über SSL/TLS
username = "raspi_all"  # MQTT Benutzername
password = "Raspi_all1"   # MQTT Passwort
topics = ["raspi/in/temp", "raspi/in/humi", "raspi/in/press", "raspi/out/temp", "raspi/out/humi", "raspi/out/press"]

# Daten-Dictionary
data = {
    "in_temp": "...",
    "in_humi": "...",
    "in_press": "...",
    "out_temp": "...",
    "out_humi": "...",
    "out_press": "..."
}

# Unit-Dictionary
units = {
    "in_temp": "°C",
    "in_humi": "%",
    "in_press": "hPa",
    "out_temp": "°C",
    "out_humi": "%",
    "out_press": "hPa"
}

# Erstellen des MQTT Clients
client = mqtt.Client("Check_Client")  # Erstellen einer MQTT-Client-Instanz
client.username_pw_set(username, password)  # Setzen von Benutzername und Passwort

# SSL/TLS Einstellungen aktivieren
client.tls_set()  # Aktivieren von SSL/TLS für sichere Kommunikation

# Callback, wenn eine Verbindung zum Broker hergestellt wurde
def on_connect(client, userdata, flags, rc):
    print("Verbunden mit dem MQTT Broker mit dem Code: " + str(rc))
    for topic in topics:
        client.subscribe(topic)

# Callback, wenn eine Verbingung zum Broker hergestellt wurde
def on_message(client, userdata, msg):
    topic = msg.topic
    payload = json.loads(msg.payload.decode())
    
    # Aktualisierung der entsprechenden Sensorwerte basierend auf dem Topic
    if topic == "raspi/in/temp":
        data['in_temp'] = payload['temperature']
    elif topic == "raspi/in/humi":
        data['in_humi'] = payload['humidity']
    elif topic == "raspi/in/press":
        data['in_press'] = payload['pressure']
    elif topic == "raspi/out/temp":
        data['out_temp'] = payload['temperature']
    elif topic == "raspi/out/humi":
        data['out_humi'] = payload['humidity']
    elif topic == "raspi/out/press":
        data['out_press'] = payload['pressure']

# Callback Funktionen zuweisen
client.on_connect = on_connect  # Zuweisung der Callback-Funktion
client.on_message = on_message

# Initialisiere Pygame und das Display
pygame.init()
lcd_size = (480, 320)
lcd = pygame.display.set_mode(lcd_size, pygame.FULLSCREEN)
pygame.display.set_caption('Wetterstation')
pygame.mouse.set_visible(False)

# Schriftart laden
font_size = 35
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)

# Definition des Zeilenabstand
line_spacing = font_size + 5

# Funktion zur Aktualisierung der Uhrzeit
def update_time(draw):
    now = datetime.now()
    time_str = now.strftime("%d.%m.%Y %H:%M:%S")
    draw.text((10, 10), time_str, font=font, fill="white")

# Funktion zur Aktualisierung der Wetterdaten
def update_weather_data(draw):
        y_pos = 60
        for key in data:
            value = data[key]
            unit = units.get(key, "")
            text = f"{key.replace('_', ' ').title()}: {value}{unit}"
            
            # Berechnet die Breite und Höhe des Texts
            text_width, text_height = draw.textsize(text, font=font)
            
            # Berechnet die die X-Position, um den Text horizontal zentriert darzustellen
            x_pos = (lcd_size[0] - text_width) / 2
            
            # Verwendet die aktuelle Y-Position und erhöhen Sie sie um den Zeilenabstand
            draw.text((x_pos, y_pos), text, font=font, fill="white")
            
            # Erhöht die Y-Pos um den Zeilenabstand, um Platz für die nächste Zeile zu schaffen
            y_pos += line_spacing

# Display-Update Funktion
def update_display():
    # Erstellt ein schwarzes Bild im LCD-Format
    image = Image.new('RGB', lcd_size, 'black')
    draw = ImageDraw.Draw(image)
    
    # Zeichnet die aktuelle Uhrzeit und Wetterdaten auf das Bild
    update_time(draw)
    update_weather_data(draw)

    # Konvertiert das PIL-Bild in ein Pygame-Bild
    py_image = pygame.image.fromstring(image.tobytes(), image.size, image.mode)
    
    # Zeigt das Pygame-Bild auf dem LCD an
    lcd.blit(py_image, (0, 0))
    pygame.display.update()  # Aktualisiert das Display

# Verbindung zum Broker herstellen
client.connect(broker, port)  # Verbinden mit dem MQTT Broker

# Starten des MQTT-Clients im Hintergrund
client.loop_start()

# Hauptprogrammschleife
try:
    # Initialisiere die Schleifensteuerungsvariablen
    running = True  # Diese Variable behält den Zustand der Ausführung bei
    ctrl_held = False  # Diese Variable prüft, ob die Steuerungstaste gedrückt gehalten wird

    # Starte die Event-Schleife
    while running:
        # Verarbeite alle Ereignisse aus der Pygame-Ereigniswarteschlange
        for event in pygame.event.get():
            # Wenn der Benutzer das Pygame-Fenster schließt
            if event.type == pygame.QUIT:
                running = False  # Beendet die Schleife, um das Programm zu beenden
            # Wenn eine Taste gedrückt wird
            elif event.type == pygame.KEYDOWN:
                # Überprüfe, ob eine der Steuerungstasten gedrückt wurde
                if event.key == pygame.K_LCTRL or event.key == pygame.K_RCTRL:
                    ctrl_held = True  # Steuerungstaste wird als gedrückt markiert
                # Wenn 'C' gedrückt wird, während die Steuerungstaste gehalten wird
                elif event.key == pygame.K_c and ctrl_held:
                    running = False  # Beendet die Schleife, um das Programm zu beenden
            # Wenn eine Taste losgelassen wird
            elif event.type == pygame.KEYUP:
                # Setze die Steuerungstaste zurück, wenn sie losgelassen wird
                if event.key == pygame.K_LCTRL or event.key == pygame.K_RCTRL:
                    ctrl_held = False

        # Aktualisiert das Display mit neuen Daten
        update_display()
        # Warte 1 Sekunde vor der nächsten Aktualisierung
        time.sleep(1)

# Fängt das KeyboardInterrupt-Ereignis ab, das ausgelöst wird, wenn Ctrl+C im Terminal gedrückt wird
except KeyboardInterrupt:
    print("Programm wird beendet")

# Dieser Block wird immer ausgeführt, auch wenn ein Fehler auftritt oder das Programm beendet wird
finally:
    # Beendet den MQTT-Client sauber, um sicherzustellen, dass keine Netzwerkressourcen offen bleiben
    client.loop_stop()  # Stoppt den Netzwerk-Thread des MQTT-Clients
    client.disconnect()  # Trennt die Verbindung zum MQTT-Broker
    pygame.quit()  # Beendt alle Pygame-Module sauber
    print("Programm erfolgreich beendet")
