import cv2
import requests
import numpy as np
from PIL import Image
from io import BytesIO

# URLs der ESP32-Cam
stream_url = "http://192.168.8.178:81/stream"  # Stream-Endpunkt
capture_url = "http://192.168.8.178/capture"   # Einzelbild-Endpunkt

# Gesichtserkennungsmodell (Haar-Cascade)
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

def fetch_image(url):
    """Einzelbild von der ESP32-Cam abrufen und Gesichter erkennen."""
    response = requests.get(url)
    if response.status_code == 200:
        img = Image.open(BytesIO(response.content))  # Bild laden
        frame = np.array(img)  # In NumPy-Array konvertieren (für OpenCV)
        
        # Gesichter erkennen
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        
        # Rechtecke um erkannte Gesichter zeichnen
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
        # Bild anzeigen
        cv2.imshow("Einzelbild mit Gesichtserkennung", frame)
        cv2.waitKey(0)  # Warten, bis eine Taste gedrückt wird
        cv2.destroyAllWindows()
    else:
        print(f"Fehler beim Abrufen des Einzelbildes: {response.status_code}")

def stream_camera(url):
    """MJPEG-Stream abrufen und Gesichter erkennen."""
    stream = requests.get(url, stream=True)
    if stream.status_code != 200:
        print(f"Fehler beim Abrufen des Streams: {stream.status_code}")
        return

    bytes_data = b""
    try:
        for chunk in stream.iter_content(chunk_size=1024):
            bytes_data += chunk
            start = bytes_data.find(b'\xff\xd8')  # JPEG-Startmarker
            end = bytes_data.find(b'\xff\xd9')    # JPEG-Endmarker
            if start != -1 and end != -1:
                jpg = bytes_data[start:end+2]
                bytes_data = bytes_data[end+2:]


                if not jpg:
                    #print("Warnung: Leerer Frame empfangen!")
                    continue
                # Bild dekodieren
                frame = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)

                if frame is None:
                    #qprint("Warnung: Frame konnte nicht dekodiert werden!")
                    continue
                # Gesichter erkennen
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

                # Rechtecke um erkannte Gesichter zeichnen
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                # Frame anzeigen
                cv2.imshow("ESP32 Stream mit Gesichtserkennung", frame)

                # Mit 'q' beenden
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
    finally:
        cv2.destroyAllWindows()

# Benutzer wählt Modus
print("Wähle Modus: [1] Live-Stream oder [2] Einzelbild")
mode = input("Eingabe: ")

if mode == "1":
    print("Starte Live-Stream...")
    stream_camera(stream_url)
elif mode == "2":
    print("Hole Einzelbild...")
    fetch_image(capture_url)
else:
    print("Ungültige Eingabe!")
