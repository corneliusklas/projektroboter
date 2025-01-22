import pygame
import threading
import time
import math
import bluetooth_face  # Import für den realen Roboterkopf

running = True  # Globale Laufvariable für die GUI

# Initialisiere die Variablen am Anfang
start_u = None
start_w = None

# Konstanten
sizex = 1024
sizey = 600

# Positionen für Gesichtselemente (als Werte zwischen 0 und 1)
LEFT_EYE_X = 0.290  # Konstante Basisposition für linkes Auge
RIGHT_EYE_X = 0.710  # Konstante Basisposition für rechtes Auge
EYE_Y = 0.29  # Y-Position der Augen
EYEBROW_OFFSET_Y = 0.1  # Abstand der Augenbrauen über den Augen

# Variable für relative Augenposition (links/rechts)
e = 0.5  # 0 = ganz links, 1 = ganz rechts, 0.5 = Mitte

# Variablen für Lippenbögen, Augenlider und Augenbrauendrehung
l = 0  # Augenlider (0 = geschlossen, 1 = geöffnet)
u = 0.5  # Oberlippenbogen (0 = nach unten, 1 = nach oben)
w = 0.5  # Unterlippenbogen (0 = nach oben, 1 = nach unten)
b = 0  # Augenbrauendrehung (0 = nach innen, 1 = nach außen)

# LED-Zustände
led_yellow = False
led_red_green_inverted = False

# Roboterkopfdrehung
robot_rotation = 0.5  # 0-1

# Globale Variablen
global emotion
emotion = "neutral"
talking = False
talk_time = 0  # Zeit in Sekunden, die das Reden andauert
last_question = "test"
answer_text = "test"
base_image = None
last_update_time = None
last_emotion = None  # Zum Verfolgen der letzten Emotion

# Variable zum Speichern des letzten Zustands
last_state = {
    "l": l,
    "u": u,
    "w": w,
    "b": b,
    "e": e,
    "robot_rotation": robot_rotation,
    "led_yellow": led_yellow,
    "led_red_green_inverted": led_red_green_inverted
}

# Initialisierung der Anzeige
def init():
    global screen, base_image
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((sizex, sizey))
    pygame.display.set_caption("Robot Head")
    base_image = pygame.image.load("face/base.png")
    base_image = pygame.transform.scale(base_image, (sizex, sizey))

# Funktion zur Synchronisation mit dem realen Roboterkopf
def sync_with_real_robot():
    global last_state

    # Überprüfen, ob sich eine Variable geändert hat und nur diese senden
    if l != last_state["l"]:
        bluetooth_face.move("l", l)
        last_state["l"] = l

    if u != last_state["u"]:
        bluetooth_face.move("u", u)
        last_state["u"] = u

    if w != last_state["w"]:
        bluetooth_face.move("w", w)
        last_state["w"] = w

    if b != last_state["b"]:
        bluetooth_face.move("b", b)
        last_state["b"] = b

    if e != last_state["e"]:
        bluetooth_face.move("e", e)
        last_state["e"] = e

    if robot_rotation != last_state["robot_rotation"]:
        bluetooth_face.move("r", robot_rotation)  # Skalierung zwischen 0 und 1
        last_state["robot_rotation"] = robot_rotation

    if led_yellow != last_state["led_yellow"]:
        bluetooth_face.move("y", 1 if led_yellow else 0)
        last_state["led_yellow"] = led_yellow

    if led_red_green_inverted != last_state["led_red_green_inverted"]:
        bluetooth_face.move("g", 1 if not led_red_green_inverted else 0)
        last_state["led_red_green_inverted"] = led_red_green_inverted


# Funktion zur Verarbeitung von Bewegungen (wie beim physischen Roboterkopf)
def move(key, position):
    global l, u, w, b, robot_rotation, led_yellow, led_red_green_inverted, e

    if key == "e":  # Augenposition
        e = position  # e zwischen 0 und 1
    elif key == "l":  # Augenlider
        l = position
    elif key == "u":  # Oberlippe
        u = position
        #stelle sicher, dass die unterlippe nicht über der oberlippe liegt
        if w > u:
            w = u
    elif key == "w":  # Unterlippe
        w = position
    elif key == "b":  # Augenbrauen
        b = position   # 
    elif key == "r":  # Kopfdrehung
        robot_rotation = position
    elif key == "g":  # LED Rot/Grün
        led_red_green_inverted = bool(position)
    elif key == "y":  # LED Gelb
        led_yellow = bool(position)
    else:
        print(f"Unbekanntes Steuerzeichen: {key}")

#function to start talking
def start_talking(_talk_time):
    global talking, talk_time
    talking = True
    talk_time = _talk_time  # Beispiel: 5 Sekunden Sprechen

# Funktion zur Verarbeitung aller Tasteneingaben
def process_inputs():
    global emotion, talking, l, u, w, b, e, robot_rotation, led_yellow, led_red_green_inverted, talk_time
    global running

    if not pygame.get_init():  # Überprüfen, ob Pygame noch aktiv ist
        return

    pressed = pygame.key.get_pressed()  # Abfrage aller gedrückten Tasten

    # Emotionen wechseln
    if pressed[pygame.K_1]:
        emotion = "angry"
        print("Emotion gesetzt auf: angry")
    elif pressed[pygame.K_2]:
        emotion = "happy"
        print("Emotion gesetzt auf: happy")
    elif pressed[pygame.K_3]:
        emotion = "sad"
        print("Emotion gesetzt auf: sad")
    elif pressed[pygame.K_4]:
        emotion = "neutral"
        print("Emotion gesetzt auf: neutral")

    # Talking aktivieren
    if pressed[pygame.K_a]:  # Taste A startet das Sprechen
        start_talking(5)
        print("Reden gestartet")

    # Augenlider steuern
    if pressed[pygame.K_q]:
        move("l", max(0, l - 0.03))  # Augenlider schließen
    elif pressed[pygame.K_w]:
        move("l", min(1, l + 0.03))  # Augenlider öffnen

    # Oberlippenbewegung
    if pressed[pygame.K_e]:
        move("u", min(1, u + 0.05))  # Oberlippe nach oben
    elif pressed[pygame.K_r]:
        move("u", max(0, u - 0.05))  # Oberlippe nach unten

    # Unterlippenbewegung
    if pressed[pygame.K_t]:
        move("w", min(1, w + 0.05))  # Unterlippe nach unten
    elif pressed[pygame.K_z]:
        move("w", max(0, w - 0.05))  # Unterlippe nach oben

    # Augenbrauendrehung
    if pressed[pygame.K_s]:
        move("b", min(1, b + 0.1))  # Augenbrauen nach außen drehen
    elif pressed[pygame.K_d]:
        move("b", max(0, b - 0.1))  # Augenbrauen nach innen drehen

    # Augen horizontal bewegen
    if pressed[pygame.K_LEFT]:
        move("e", max(0, e - 0.1))  # Augen nach links
    elif pressed[pygame.K_RIGHT]:
        move("e", min(1, e + 0.1))  # Augen nach rechts

    # LEDs steuern
    if pressed[pygame.K_f]:
        move("g", not led_red_green_inverted)  # Rot/Grün invertieren
    if pressed[pygame.K_g]:
        move("y", not led_yellow)  # Gelbe LED umschalten

    # Roboterkopfdrehung steuern
    if pressed[pygame.K_y]:
        move("r", min(1, robot_rotation + 0.05))  # Kopf im Uhrzeigersinn
    elif pressed[pygame.K_x]:
        move("r", max(0, robot_rotation - 0.05))  # Kopf gegen den Uhrzeigersinn

    return True



# Funktion zur Ereignisverarbeitung
def handle_events():
    global running
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False  # Setze den globalen Laufstatus auf False
            return False
    return True

# Funktion zur Aktualisierung der Positionen basierend auf der Emotion und dem Reden
def update_positions_based_on_emotion_and_talking(emotion):
    global u, w, b, talk_time, talking, last_update_time, last_emotion, start_u, start_w

    current_time = time.time()
    if last_update_time is None:
        last_update_time = current_time
    elapsed_time = current_time - last_update_time
    last_update_time = current_time

    if emotion != last_emotion:
        # Emotion einmalig die Werte setzen
        if emotion == "happy":
            move("b", 1)  # Augenbrauen in A form
            move("u", 0) # lachen
            move("w", 0)
            #augen weit offen
            move("l", 1)
        elif emotion == "angry":
            move("b", 0)  # Augenbrauen in V Form
            move("u", 1) # mund etwas offen und nach unten
            move("w", .8)
            # augen zugekniffen
            move("l", 0.3)
        elif emotion == "sad":
            move("b", 1)  # Augenbrauen in a form
            move("u", 1)
            move("w", 1)
        elif emotion == "neutral":
            move("b", 0.5)  # Augenbrauen horizontal
            move("u", 0.5)
            move("w", 0.5)
        elif emotion == "sleepy":
            move("l", 0.1)

        #wenn gerade geredet wird: passe auch startwerte an
        if talking:
            #if 'start_u' in globals():
                #global start_u, start_w
            start_u = u
            start_w = w

        last_emotion = emotion

    if talking:
        # Lippen bewegen sich während des Redens, basierend auf der aktuellen Position
        if talk_time > 0:
            amplitude = 0.2  # Maximale Amplitude der Bewegung
            speed = 1.5  # Geschwindigkeit der Bewegung in Hertz

            # Speichere die ursprünglichen Werte von u und w, falls noch nicht gespeichert
            if start_u is None: #if 'start_u' not in globals():
                #global start_u, start_w
                start_u = u
                start_w = w
                #stelle sicher, dass es einen abstand zur bewegungsgrenze gibt
                delta = amplitude
                if u < delta:
                    start_u = delta
                if u > 1-delta:
                    start_u = 1-delta
                if w < delta:
                    start_w = delta
                if w > 1-delta:
                    start_w = 1-delta  



            time_fraction = (talk_time % (1 / speed)) * speed  # Normierte Zeit innerhalb eines Bewegungszyklus

            # Berechne die neue Position für Ober- und Unterlippe
            new_u = start_u + amplitude * math.sin(2 * math.pi * time_fraction) + amplitude/2
            new_w = start_w - amplitude * math.sin(2 * math.pi * time_fraction) - amplitude/2

            move("u", new_u)  # Aktualisiere die Oberlippenposition
            move("w", new_w)  # Aktualisiere die Unterlippenposition

            talk_time -= elapsed_time
        else:
            talking = False  # Beende das Sprechen, wenn die Zeit abgelaufen ist
            #setze die lippen zurück
            move("u", start_u)
            move("w", start_w)
            print("Talking beendet")

            # Lösche die gespeicherten Startwerte
            #if 'start_u' in globals():
            #    del start_u
            #if 'start_w' in globals():
            #    del start_w
            start_u = None
            start_w = None



# Funktion zum Zeichnen des Mundes als Bögen
def draw_mouth(u, w):
    global screen, sizex, sizey

    mouth_width = 0.2 * sizex  # Gesamte Breite des Mundes
    mouth_height = 0.05 * sizey  # Maximale Höhe der Krümmung
    center_x = sizex / 2  # Mittelpunkt des Mundes in X-Richtung
    center_y = sizey * 0.7  # Y-Position des Mundes
    lip_offset = 0.01 * sizey  # Mindestabstand der Unterlippe zur Oberlippe

    # Positionen der Mundwinkel
    left_corner = (center_x - mouth_width / 2, center_y)
    right_corner = (center_x + mouth_width / 2, center_y)

    # Punkte für die Oberlippe
    upper_left = ((center_x - mouth_width / 4), center_y - lip_offset - mouth_height * u * 2 + mouth_height)
    upper_right = ((center_x + mouth_width / 4), center_y - lip_offset - mouth_height * u * 2 + mouth_height)

    # Punkte für die Unterlippe
    lower_left = ((center_x - mouth_width / 4), center_y + lip_offset - mouth_height * w * 2 + mouth_height)
    lower_right = ((center_x + mouth_width / 4), center_y + lip_offset - mouth_height * w * 2 + mouth_height)

    # Sicherstellen, dass die Unterlippe nicht über der Oberlippe liegt
    #min_y_upper = min(upper_left[1], upper_right[1])  # Höchster Punkt der Oberlippe
    #lower_left = (lower_left[0], max(lower_left[1], min_y_upper + lip_offset))
    #lower_right = (lower_right[0], max(lower_right[1], min_y_upper + lip_offset))

    # Oberlippe zeichnen (3 Segmente)
    pygame.draw.line(screen, (100, 100, 100), left_corner, upper_left, 2)
    pygame.draw.line(screen, (100, 100, 100), upper_left, upper_right, 2)
    pygame.draw.line(screen, (100, 100, 100), upper_right, right_corner, 2)

    # Unterlippe zeichnen (3 Segmente)
    pygame.draw.line(screen, (0, 0, 0), left_corner, lower_left, 2)
    pygame.draw.line(screen, (0, 0, 0), lower_left, lower_right, 2)
    pygame.draw.line(screen, (0, 0, 0), lower_right, right_corner, 2)

# Funktion zum Zeichnen der LEDs
def draw_leds():
    global screen, sizex, sizey, led_yellow, led_red_green_inverted

    led_radius = 0.02 * sizex

    # Rote LED
    red_color = (255, 0, 0) if led_red_green_inverted else (100, 100, 100)
    pygame.draw.circle(screen, red_color, (int(0.1 * sizex), int(0.9 * sizey)), int(led_radius))

    # Grüne LED
    green_color = (0, 255, 0) if not led_red_green_inverted else (100, 100, 100)
    pygame.draw.circle(screen, green_color, (int(0.2 * sizex), int(0.9 * sizey)), int(led_radius))

    # Gelbe LED
    yellow_color = (255, 255, 0) if led_yellow else (100, 100, 100)
    pygame.draw.circle(screen, yellow_color, (int(0.3 * sizex), int(0.9 * sizey)), int(led_radius))



# Funktion zum Zeichnen des Kompasses
def draw_compass():
    global screen, sizex, sizey, robot_rotation

    compass_radius = 0.05 * sizex
    center_x = int(0.9 * sizex)
    center_y = int(0.1 * sizey)

    # Hintergrund des Kompasses
    pygame.draw.circle(screen, (200, 200, 200), (center_x, center_y), int(compass_radius))

    # Pfeil des Kompasses
    arrow_length = 0.04 * sizex
    arrow_angle = math.radians(robot_rotation*180+180)

    end_x = center_x + arrow_length * math.cos(arrow_angle)
    end_y = center_y - arrow_length * math.sin(arrow_angle)

    pygame.draw.line(screen, (0, 0, 255), (center_x, center_y), (end_x, end_y), 3)


# Funktion zum Zeichnen des Gesichts basierend auf Positionen
def draw_face():
    global screen, sizex, sizey, base_image, l, u, w, e

    # Hintergrundbild zeichnen
    screen.blit(base_image, (0, 0))

    # Augen zeichnen
    pygame.draw.circle(screen, (0, 0, 0),
                       ((LEFT_EYE_X + (e - 0.5) * 0.1) * sizex, EYE_Y * sizey), 0.01 * sizex)
    pygame.draw.circle(screen, (0, 0, 0),
                       ((RIGHT_EYE_X + (e - 0.5) * 0.1) * sizex, EYE_Y * sizey), 0.01 * sizex)

    # Variablen für maximale Breite und Höhe der Augenlider
    lid_max_width = 0.1 * sizex  # Maximale Breite der Augenlider
    lid_max_height = 0.12 * sizey  # Maximale Höhe der Augenlider

    # Augenlider zeichnen
    lid_height = (1 - l) * lid_max_height  # Augenlid-Höhe basierend auf l

    # Oberes Augenlid
    pygame.draw.rect(screen, (200, 200, 200), (
        (LEFT_EYE_X + (e - 0.5) * 0.1) * sizex - lid_max_width / 2,
        EYE_Y * sizey - lid_max_height / 2,
        lid_max_width,
        lid_height / 2
    ))
    pygame.draw.rect(screen, (200, 200, 200), (
        (RIGHT_EYE_X + (e - 0.5) * 0.1) * sizex - lid_max_width / 2,
        EYE_Y * sizey - lid_max_height / 2,
        lid_max_width,
        lid_height / 2
    ))

    # Unteres Augenlid
    pygame.draw.rect(screen, (200, 200, 200), (
        (LEFT_EYE_X + (e - 0.5) * 0.1) * sizex - lid_max_width / 2,
        EYE_Y * sizey + lid_max_height / 2 - lid_height / 2,
        lid_max_width,
        lid_height / 2
    ))
    pygame.draw.rect(screen, (200, 200, 200), (
        (RIGHT_EYE_X + (e - 0.5) * 0.1) * sizex - lid_max_width / 2,
        EYE_Y * sizey + lid_max_height / 2 - lid_height / 2,
        lid_max_width,
        lid_height / 2
    ))

    # Augenbrauen zeichnen
    draw_eyebrows()

    # Lippen zeichnen
    draw_mouth(u, w)

    # LEDs zeichnen
    draw_leds()

    # Kompass zeichnen
    draw_compass()

    # Antworttext anzeigen
    font = pygame.font.SysFont('Arial', int(0.03 * sizex))
    text1 = font.render(last_question, True, (0, 0, 0))
    text2 = font.render(answer_text, True, (0, 0, 0))
    screen.blit(text1, (0.05 * sizex, 0.92 * sizey))
    screen.blit(text2, (0.05 * sizex, 0.94 * sizey))

    pygame.display.flip()

# Funktion zum Zeichnen der Augenbrauen
def draw_eyebrows():
    global screen, sizex, sizey, b

    eyebrow_length = 0.1 * sizex
    eyebrow_height = 0.02 * sizey

    # Augenbrauenpositionen relativ zur festen Basis
    left_center_x = LEFT_EYE_X * sizex
    left_center_y = (EYE_Y - EYEBROW_OFFSET_Y) * sizey

    right_center_x = RIGHT_EYE_X * sizex
    right_center_y = (EYE_Y - EYEBROW_OFFSET_Y) * sizey

    # Berechnung der Rotation der Augenbrauen basierend auf b
    left_dx = eyebrow_length * math.cos(math.radians(+40-80 * b))
    left_dy = eyebrow_height * math.sin(math.radians(+40-80 * b))

    right_dx = eyebrow_length * math.cos(math.radians(-40+80 * b))
    right_dy = eyebrow_height * math.sin(math.radians(-40+80 * b))

    # Linke Augenbraue zeichnen
    pygame.draw.line(screen, (0, 0, 0),
                     (left_center_x - left_dx, left_center_y - left_dy),
                     (left_center_x + left_dx, left_center_y + left_dy), 2)

    # Rechte Augenbraue zeichnen
    pygame.draw.line(screen, (0, 0, 0),
                     (right_center_x - right_dx, right_center_y - right_dy),
                     (right_center_x + right_dx, right_center_y + right_dy), 2)


def play_sequence(sequence, loop=False):
    """
    Spielt eine Sequenz von Bewegungen ab.

    Args:
        sequence (list): Liste von Bewegungen, z. B.:
            [
                {"l": current, "pause": 2},
                {"l": 0, "pause": 0.5}
            ]
        loop (bool): Wiederholt die Sequenz, wenn True.
    """
    # Speichert die ursprünglichen Werte der Variablen
    saved_values = {
        "l": l,
        "u": u,
        "w": w,
        "b": b,
        "e": e,
        "robot_rotation": robot_rotation,
        "led_yellow": led_yellow,
        "led_red_green_inverted": led_red_green_inverted,
    }

    def execute_sequence():
        global l, u, w, b, e, robot_rotation, led_yellow, led_red_green_inverted

        while True:
            for step in sequence:
                # Bewegungseinstellungen anwenden
                for key in step:
                    if key == "pause":
                        continue  # Pause wird separat behandelt
                    if step[key] == "current":
                        # Speichere den aktuellen Wert, falls nicht bereits gespeichert
                        move(key, saved_values[key])
                    else:
                        #speichere den vorherigen wert
                        saved_values[key] = globals()[key]
                        #print("saved value",saved_values[key])
                        #print("new value",step[key])
                        # Setze den Wert der Variable
                        move(key, step[key])
    

                # Pause
                pause = step.get("pause", 0)
                if pause > 0:
                    time.sleep(pause)

            # Nach der Sequenz die ursprünglichen Werte wiederherstellen
            #for key, value in saved_values.items():
            #    if key in globals():
            #        move(key, value)

            if not loop:
                break

    # Starte die Sequenz in einem separaten Thread
    sequence_thread = threading.Thread(target=execute_sequence, daemon=True)
    sequence_thread.start()

# Idle Bewegungssequenz
sequence = [
    {"l": 0, "pause": 0.5},
    {"l": "current", "pause": 5},
    {'e': 0.1, 'pause': 0.5},
    {'e': 0.9, 'pause': 0.5},
    {'e': 0.5, 'pause': 0.5},
]

BLUETOOTH=True

# GUI ausführen
def run_gui():
    global running
    init()

    try:
        # Sequenz abspielen
        play_sequence(sequence, loop=True)
        if BLUETOOTH:
            bluetooth_face.init()
            move("l", 1)

        while running:
            if not handle_events():
                break
            draw_face()
            update_positions_based_on_emotion_and_talking(emotion)
            if BLUETOOTH:
                sync_with_real_robot()
            time.sleep(0.01)

    finally:
        # Sicherstellen, dass die GUI beendet wird
        running = False  # Beende die Schleife sicher
        pygame.quit()  # Pygame sauber beenden

# Hauptprogramm bei standalone-Ausführung
def standalone_main():
    global running

    gui_thread = threading.Thread(target=run_gui, daemon=True)
    gui_thread.start()

    try:
        while running:
            process_inputs()
            time.sleep(0.01)
    finally:
        running = False  # Beende sicher die Schleifen
        gui_thread.join()  # Warte auf den GUI-Thread, bevor das Programm endet

if __name__ == "__main__":
    standalone_main()
