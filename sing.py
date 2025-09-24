


# play_and_drive_robot.py
# Spielt instrumental.mp3 + robotvoice.mp3 ab und steuert den Roboter synchron zur Musik.
# Voraussetzungen (empfohlen): pip install librosa numpy
# Alternativ/Fallback: pip install pydub numpy  (benötigt ffmpeg)

import threading
import time
import math
import os
import sys
import random

# --- Eure bestehende Datei importieren (den Namen ggf. anpassen!) ---
# Die Datei mit der GUI/Funktionen aus deiner Nachricht sollte als "gui_face.py" (oder ähnlich) vorliegen.
# Passen Sie den Import unten an den tatsächlichen Dateinamen an.
import pygame
try:
    import gui_face as rh  # <- HIER ggf. anpassen, z.B. "import robot_head as rh"
except ImportError:
    print("Konnte 'gui_face' nicht importieren. Bitte Dateiname im Import anpassen.")
    raise

# Versuche Audio-Analyse-Backends zu laden
BACKEND = None
try:
    import numpy as np
    import librosa
    BACKEND = "librosa"
except Exception:
    try:
        import numpy as np
        from pydub import AudioSegment
        BACKEND = "pydub"
    except Exception:
        BACKEND = "none"

# ------------------------ Parameter ------------------------
VOICE_FILE = "voice.wav"
MUSIC_FILE = "music.mp3"
print("aktueller Pfad:", os.getcwd())
print("Suche voice:", os.path.exists(VOICE_FILE), VOICE_FILE)
print("Suche musik:", os.path.exists(MUSIC_FILE), MUSIC_FILE)

SR = 22050            # Sample-Rate für Analyse (librosa)
HOP_LENGTH = 512      # Hop für Hüllkurve/Beats
MOUTH_GAIN = 1    # wie stark die Lippen auf Lautstärke reagieren (0..~0.5)
HEAD_BOB_FREQ = 0.5   # Hz Basis-"Nicken"
HEAD_BOB_AMP  = 0.05  # Amplitude fürs Nicken
BEAT_PULSE_DURATION = 0.12  # 0.12Sekunden: wie lang Beat-Pulse dauern
BEAT_PULSE_STRENGTH = 0.18  # Stärke des Beat-Impulses für Augenbrauen/LEDs
FPS = 25

# ------------------------ Analyse-Funktionen ------------------------
def analyze_with_librosa(path_voice, path_music):
    # Voice: RMS-Hüllkurve
    yv, srv = librosa.load(path_voice, sr=SR, mono=True)
    rms = librosa.feature.rms(y=yv, frame_length=2048, hop_length=HOP_LENGTH)[0]
    rms = rms / (np.max(rms) + 1e-9)

    # Musik: Onsets/Beats
    ym, srm = librosa.load(path_music, sr=SR, mono=True)
    onset_env = librosa.onset.onset_strength(y=ym, sr=SR, hop_length=HOP_LENGTH)
    tempo, beats = librosa.beat.beat_track(onset_envelope=onset_env, sr=SR, hop_length=HOP_LENGTH)
    beat_times = librosa.frames_to_time(beats, sr=SR, hop_length=HOP_LENGTH)
    return rms, beat_times

def analyze_with_pydub(path_voice, path_music):
    # Sehr einfache RMS-Hüllkurve (Fenster) via pydub
    seg_v = AudioSegment.from_file(path_voice)
    seg_m = AudioSegment.from_file(path_music)

    # Hop in ms
    hop_ms = int(1000 * HOP_LENGTH / SR)
    hop_ms = max(5, hop_ms)

    # Voice RMS
    rms_vals = []
    for pos in range(0, len(seg_v), hop_ms):
        chunk = seg_v[pos:pos+hop_ms]
        rms_vals.append(chunk.rms)
    rms_vals = np.array(rms_vals, dtype=float)
    if rms_vals.max() > 0:
        rms_vals = rms_vals / rms_vals.max()
    else:
        rms_vals[:] = 0

    # Beat-Schätzung: einfache Onset-Heuristik über Lautheitsdifferenz
    loud = []
    for pos in range(0, len(seg_m), hop_ms):
        chunk = seg_m[pos:pos+hop_ms]
        loud.append(chunk.rms)
    loud = np.array(loud, dtype=float)
    # Onset wenn signifikanter Anstieg
    onset = np.diff(loud, prepend=loud[0])
    thresh = loud.mean() * 0.08 + onset.std() * 0.5
    beat_frames = np.where(onset > thresh)[0]
    beat_times = (beat_frames * hop_ms) / 1000.0
    return rms_vals, beat_times

def analyze_audio(path_voice, path_music):
    if BACKEND == "librosa":
        print("Analyse-Backend: librosa")
        return analyze_with_librosa(path_voice, path_music)
    elif BACKEND == "pydub":
        print("Analyse-Backend: pydub")
        return analyze_with_pydub(path_voice, path_music)
    else:
        print("Ohne Analyse-Backend – es wird ein musikalischer Fallback genutzt.")
        return None, None

# ------------------------ Playback + Steuerung ------------------------
def play_and_drive():
    # Startet eure GUI (falls nicht schon durch __main__ in eurer Datei)
    # Wir starten einen separaten Thread, analog zu standalone_main()
    gui_thread = threading.Thread(target=rh.run_gui, daemon=True)
    gui_thread.start()
    time.sleep(0.3)

    # Audio vorbereiten
    pygame.mixer.init()
    if not os.path.exists(MUSIC_FILE) or not os.path.exists(VOICE_FILE):
        print("Fehlende Dateien! Stelle sicher, dass die dateien im gleichen Ordner liegen.")
        return

    music = pygame.mixer.Sound(MUSIC_FILE)
    voice = pygame.mixer.Sound(VOICE_FILE)

    ch_music = pygame.mixer.Channel(0)
    ch_voice = pygame.mixer.Channel(1)

    # Analyse-Daten (können None sein, dann Fallback)
    voice_env, beat_times = analyze_audio(VOICE_FILE, MUSIC_FILE)

    # Startzeit für Sync
    start_t = time.monotonic()

    # Abspielen
    ch_music.play(music)
    ch_voice.play(voice)

    # Zustände
    beat_index = 0
    last_beat_pulse_until = 0.0

    # Start-Defaults
    rh.move("l", 1)       # Augen offen
    rh.move("u", 0.5)     # Lippen neutral
    rh.move("w", 0.5)
    rh.move("b", 0.5)     # Augenbrauen neutral
    rh.move("e", 0.5)     # Blick Mitte
    rh.move("v", 0.5)
    rh.move("r", 0.5)     # Kopf Mitte
    rh.move("y", 0)       # Gelb aus
    rh.move("g", 0)       # Rot/Grün Standard (nicht invertiert)

    def env_at(t):
        # Lautstärke-Hüllkurve zum Zeitpunkt t
        if voice_env is None:
            # Fallback: pseudo-rhythmische Kurve
            return 0.25 + 0.25 * (0.5 + 0.5 * math.sin(2 * math.pi * 2.0 * t + 0.7))
        # Mapping Zeit -> Frame
        frame = int((t * SR) / HOP_LENGTH)
        if frame < 0:
            frame = 0
        if frame >= len(voice_env):
            frame = len(voice_env) - 1
        return float(voice_env[frame])

    def is_beat_now(t):
        nonlocal beat_index, last_beat_pulse_until
        if beat_times is None or beat_index >= (len(beat_times) if beat_times is not None else 0):
            return False
        if t >= beat_times[beat_index]:
            # Beat erkannt
            last_beat_pulse_until = t + BEAT_PULSE_DURATION
            beat_index += 1
            return True
        return False

    # Haupt-Steuerschleife während Audio läuft
    clock = pygame.time.Clock()
    while ch_music.get_busy() or ch_voice.get_busy():
        t = time.monotonic() - start_t

        # --- Beats prüfen & Pulse setzen ---
        beat_hit = is_beat_now(t)
        beat_pulse_active = t < last_beat_pulse_until

        # --- Lippen aus Voice-Hüllkurve ---
        a = env_at(t) * MOUTH_GAIN  # 0..~0.5
        # kleine Glättung:
        a = max(0.0, min(0.48, a))

        # Baseline leicht öffnen, damit man Bewegung sieht
        base = 0.48
        u = base + a
        w = base - a
        u = max(0.0, min(1.0, u))
        w = max(0.0, min(1.0, w))

        rh.move("u", u)
        rh.move("w", w)

        # --- Kopfbewegung: sanftes Nicken + kleiner Beat-Schub ---
        head = 0.5 + HEAD_BOB_AMP * math.sin(2 * math.pi * HEAD_BOB_FREQ * t)
        if beat_pulse_active:
            head += 0.03
        head = max(0.0, min(1.0, head))
        rh.move("r", head)

        # --- Augenbrauen: Pulse auf Beat ---
        brow = 0.5 + (BEAT_PULSE_STRENGTH if beat_pulse_active else 0.0)
        brow = max(0.0, min(1.0, brow))
        rh.move("b", brow)

        # --- LEDs: Gelb blinkt auf Beats, Rot/Grün invertiert wechselt langsam ---
        rh.move("y", 1 if beat_pulse_active else 0)
        # langsames „Atmen“ der Rot/Grün-LED (invertiert toggeln)
        if int(t) % 4 == 0:
            rh.move("g", 1)
        else:
            rh.move("g", 0)

        # Optional: Augen leicht horizontal pendeln
        eye_x = 0.5 + 0.08 * math.sin(2 * math.pi * 0.2 * t + 1.2)
        eye_y = 0.5 + 0.05 * math.sin(2 * math.pi * 0.17 * t)
        rh.move("e", max(0.0, min(1.0, eye_x)))
        rh.move("v", max(0.0, min(1.0, eye_y)))

        # Kleine Pause auf ~FPS
        clock.tick(FPS)

    # Audio zu Ende – zurück auf neutral
    rh.move("u", 0.5)
    rh.move("w", 0.5)
    rh.move("b", 0.5)
    rh.move("e", 0.5)
    rh.move("v", 0.5)
    rh.move("r", 0.5)
    rh.move("y", 0)
    rh.move("g", 0)
    print("Fertig – Playback beendet.")

# ------------------------ main ------------------------
if __name__ == "__main__":
    # Stelle sicher, dass die Dateien existieren
    for f in (MUSIC_FILE, VOICE_FILE):
        if not os.path.exists(f):
            print(f"Fehlt: {f}")
    play_and_drive()


