#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
wlan_face.py
Steuert den Roboterkopf über den ESP32-WebSocket-Endpunkt (/ws).

Voraussetzung:
    pip install websocket-client

Tastenbelegung (CLI):
  Augen L/R:   'q' = links (-0.25), 'w' = rechts (+0.25)
  Augen U/D:   'e' = hoch(-0.25),  'r' = runter(+0.25)
  Lider:       't' = auf(1),       'z' = zu(0)
  Oberlippe:   'u' = hoch(1),      'i' = runter(0)
  Unterlippe:  'o' = hoch(1),      'p' = runter(0)
  Brauen:      'a' = hoch(1),      's' = runter(0)
  Neutral:     '0' setzt alle gemappten Servos auf 90°
  Filter:      'f <0..1>' (z.B. 'f 0.85')
  Hilfe:       '?'   Beenden: 'x'

Kompatible Programmierschnittstelle (wie bluetooth_face.move):
  move('e', pos)  -> Augen links/rechts (LR)
  move('v', pos)  -> Augen hoch/runter (TB)   ← NEU (v = vertical)
  move('l', pos)  -> Lider
  move('b', pos)  -> Brauen
  move('u', pos)  -> Oberlippe (Kollisionsschutz)
  move('w', pos)  -> Unterlippe (Kollisionsschutz)
  move('g', pos)  -> LED grün/rot
  move('y', pos)  -> LED gelb
  move('r', pos)  -> (Rotation momentan ohne Wirkung)
"""

import time
import json
import threading
from typing import Dict, Tuple, List, Optional
from math import isfinite

import websocket  # websocket-client

# ------------------ KONFIG ------------------

import config
WS_URL = config.WS_URL

PRINT_DEBUG = False
PRINT_SENSORS = False
PRINT = False  # für move()-Kompatibilität

# Logische Kanäle → Servo-Indices im ESP32 (0..N-1)
MAP: Dict[str, List[int]] = {
    "upper":   [0],  # Oberlippe
    "lower":   [1],  # Unterlippe
    "eyesLR":  [2],  # Augen links/rechts
    "eyesTB":  [3],  # Augen oben/unten
    "lids":    [4],  # Lider auf/zu
    "brows":   [5],  # Brauen/Antennen
    # "head": [X],   # Rotation kommt später
}

# individuelle Kalibrierung je Servoindex (min_deg, max_deg)
CAL: Dict[int, Tuple[int, int]] = {
    0: (135, 67),  #  unten 0- oben 1
    1: (108, 180),  # unten 0 - oben 1
    2: (140, 57),  # links - rechts
    3: (81, 38),   # oben - unten
    4: (128, 67),  # zu - auf
    5: (77, 180),  # hoch - runter
}

# LED-Indizes wie im ESP32-Sketch
LED_GREEN_IDX = 0
LED_YELLOW_IDX = 2

# Schrittweiten (für die inkrementellen Augenbewegungen)
STEP = 0.25

# ------------------ STATE -------------------
import queue

class State:
    def __init__(self):
        self.eyes_lr = 0.5
        self.eyes_tb = 0.5
        self.upper_pos = 0.0
        self.lower_pos = 0.0
        self.connected = False
        self.ws_app: Optional[websocket.WebSocketApp] = None
        self.ws_lock = threading.Lock()
        self.stop_evt = threading.Event()
        self._ws_started = False
        self.queue = queue.Queue(maxsize=100)  # Nachrichten-Warteschlange

STATE = State()

# ------------------ HILFSFUNKTIONEN ------------------

def clamp(x: float, a: float = 0.0, b: float = 1.0) -> float:
    try:
        if not isfinite(x):
            return a
    except Exception:
        return a
    return max(a, min(b, x))

def pos_to_deg(idx: int, pos01: float) -> int:
    """Mappt 0..1 auf (min,max) aus CAL; funktioniert auch bei umgedrehter Richtung."""
    pos01 = clamp(pos01, 0.0, 1.0)
    mn, mx = CAL.get(idx, (0, 180))
    deg_f = mn + pos01 * (mx - mn)
    lo, hi = (mn, mx) if mn <= mx else (mx, mn)
    return int(round(max(lo, min(hi, deg_f))))

def send_ws(text: str):
    if PRINT_DEBUG:
        print("queue >>", text)
    # Fallback: enqueue non-coalesced messages (best-effort).
    # If the queue is full, remove the oldest element and insert the new one
    # so we keep the most recent commands (drop oldest).
    try:
        try:
            STATE.queue.put_nowait(text)
        except queue.Full:
            # Drop the oldest item to make room for the new one
            try:
                _ = STATE.queue.get_nowait()
            except queue.Empty:
                pass
            try:
                STATE.queue.put_nowait(text)
            except queue.Full:
                # If it still fails, give up
                if PRINT_DEBUG:
                    print("queue still full, drop:", text)
    except Exception:
        # any unexpected error -> drop
        if PRINT_DEBUG:
            print("queue put error/drop:", text)

def sender_worker():
    # Minimum interval between two sends (seconds). Tuneable to avoid flooding
    # the ESP32. 0.02 => 50 Hz, 0.05 => 20 Hz. Use a conservative default.
    WS_MSG_MIN_INTERVAL = 0.01

    while not STATE.stop_evt.is_set():
        try:
            msg = STATE.queue.get(timeout=0.1)
        except queue.Empty:
            continue
        with STATE.ws_lock:
            ws = STATE.ws_app
            if ws and STATE.connected:
                try:
                    ws.send(msg)
                    if PRINT_DEBUG:
                        print(">> sent:", msg)
                except Exception as e:
                    STATE.connected = False
                    if PRINT_DEBUG:
                        print("send failed, requeue:", e)
                    STATE.queue.put(msg)
            else:
                # keine Verbindung -> später nochmal probieren
                STATE.queue.put(msg)
                time.sleep(0.5)

        # Rate limiting
        time.sleep(WS_MSG_MIN_INTERVAL)

def set_servo(idx: int, deg: int):
    deg = max(0, min(180, int(deg)))
    send_ws(f"servo:{idx}:{deg}")

def set_group(name: str, pos01: float):
    for idx in MAP.get(name, []):
        set_servo(idx, pos_to_deg(idx, pos01))

def set_all_neutral():
    touched = set()
    for indices in MAP.values():
        for idx in indices:
            if idx not in touched:
                touched.add(idx)
                set_servo(idx, 90)
    STATE.eyes_lr = 0.5
    STATE.eyes_tb = 0.5
    STATE.upper_pos = 0.0
    STATE.lower_pos = 0.0

def set_filter(val: float):
    val = clamp(val, 0.0, 1.0)
    send_ws(f"filter:{val}")

def set_led(idx: int, on: bool):
    send_ws(f"led:{idx}:{1 if on else 0}")

# ------------------ WEBSOCKET CALLBACKS ------------------

def on_open(wsapp):
    STATE.connected = True
    if PRINT_DEBUG:
        print("[WS] Open")

def on_close(wsapp, status_code, msg):
    if PRINT_DEBUG:
        print(f"[WS] Close: {status_code} {msg}")
    STATE.connected = False

def on_error(wsapp, error):
    if PRINT_DEBUG:
        print("[WS] Error:", error)
    STATE.connected = False

def on_message(wsapp, message: str):
    try:
        if message and message.startswith("{"):
            data = json.loads(message)
            if PRINT_SENSORS:
                print("[SENS]", data)
    except Exception:
        pass

def ws_worker():
    while not STATE.stop_evt.is_set():
        try:
            STATE.ws_app = websocket.WebSocketApp(
                WS_URL,
                on_open=on_open,
                on_close=on_close,
                on_error=on_error,
                on_message=on_message,
            )
            STATE.ws_app.run_forever(ping_interval=5, ping_timeout=3)
        except Exception as e:
            if PRINT_DEBUG:
                print("[WS] run_forever exception:", e)
        finally:
            STATE.connected = False
            for _ in range(5):
                if STATE.stop_evt.is_set():
                    break
                time.sleep(0.1)

# ------------------ KOMPATIBILITÄT: move() ------------------

def _apply_lip_collision(upper: Optional[float] = None, lower: Optional[float] = None):
    """Sorgt dafür, dass upper_pos > lower_pos bleibt."""
    #1 hoch - 0 runter
    if upper is not None:
        STATE.upper_pos = clamp(upper)
    if lower is not None:
        STATE.lower_pos = clamp(lower)
    if STATE.lower_pos > STATE.upper_pos:
        print("Collision:", STATE.lower_pos, " > ", STATE.upper_pos) 
        STATE.lower_pos = STATE.upper_pos
        print("→ set lower_pos =", STATE.lower_pos)
    set_group("upper", STATE.upper_pos)
    set_group("lower", STATE.lower_pos)

def move(key: str, position: float):
    """
    Kompatibel zu robotface_bluetooth.move():
      'l' = Lider, 'e' = Augen L/R, 'v' = Augen U/D (NEU),
      'b' = Brauen, 'u' = Oberlippe, 'w' = Unterlippe,
      'r' = Rotation (derzeit ohne Wirkung), 'g' = LED grün/rot, 'y' = LED gelb.
    position in [0..1].
    """
    k = (key or "").lower()
    pos = clamp(float(position))

    if k == "l":        # lids
        set_group("lids", pos)
    elif k == "e":      # eyes (L/R)
        STATE.eyes_lr = pos
        set_group("eyesLR", STATE.eyes_lr)
    elif k == "v":      # eyes (vertical U/D)
        STATE.eyes_tb = pos
        set_group("eyesTB", STATE.eyes_tb)
    elif k == "b":      # brows
        set_group("brows", pos)
    elif k == "u":      # upper lip (mit Kollisionsschutz)
        _apply_lip_collision(upper=pos)
    elif k == "w":      # lower lip (mit Kollisionsschutz)
        _apply_lip_collision(lower=pos)
    elif k == "r":      # rotation: derzeit nicht vorhanden → ignorieren
        if PRINT_DEBUG:
            print("move('r', …) ignoriert: Rotation ist noch nicht implementiert.")
    elif k == "g":      # LED grün/rot
        set_led(LED_GREEN_IDX, pos >= 0.5)
    elif k == "y":      # LED gelb
        set_led(LED_YELLOW_IDX, pos >= 0.5)
    else:
        if PRINT:
            print(f"move(): unbekannter key '{key}' (pos={pos})")

# ------------------ KOMMANDO-LOGIK (CLI) ------------------

HELP = """
Steuerung:
  'q'  Augen links  (-0.25)    'w'  Augen rechts (+0.25)
  'e'  Augen hoch   (-0.25)    'r'  Augen runter (+0.25)
  't'  Lider auf (1)           'z'  Lider zu (0)
  'u'  Oberlippe hoch (1)      'i'  Oberlippe runter (0)
  'o'  Unterlippe hoch (1)     'p'  Unterlippe runter (0)
  'a'  Brauen runter (1)       's'  Brauen hoch (0)
  '0'  alle gemappten Servos auf 90°
  'f <0..1>'  Low-Pass-Filter setzen
  '?'  Hilfe anzeigen           'x'  Beenden
"""

def process_command(raw: str):
    cmd = raw.strip()
    if not cmd:
        return
    low = cmd.lower()

    if low.startswith("f "):
        try:
            val = float(low.split(" ", 1)[1])
            set_filter(val)
        except Exception:
            print("Usage: f <float 0..1>")
        return

    # Augen L/R
    if low == "q":
        STATE.eyes_lr = clamp(STATE.eyes_lr - STEP)
        set_group("eyesLR", STATE.eyes_lr)
        return
    if low == "w":
        STATE.eyes_lr = clamp(STATE.eyes_lr + STEP)
        set_group("eyesLR", STATE.eyes_lr)
        return

    # Augen U/D
    if low == "e":
        STATE.eyes_tb = clamp(STATE.eyes_tb - STEP)
        set_group("eyesTB", STATE.eyes_tb)
        return
    if low == "r":
        STATE.eyes_tb = clamp(STATE.eyes_tb + STEP)
        set_group("eyesTB", STATE.eyes_tb)
        return

    # Lider
    if low == "t":
        set_group("lids", 1.0)
        return
    if low == "z":
        set_group("lids", 0.0)
        return

    # Lippen (mit Kollisionsschutz)
    if low == "u":
        _apply_lip_collision(upper=1.0)
        print("upper = 1.0")
        return
    if low == "i":
        _apply_lip_collision(upper=0.0)
        print("upper = 0.0")
        return
    if low == "o":
        _apply_lip_collision(lower=1.0)
        print("lower = 1.0")
        return
    if low == "p":
        _apply_lip_collision(lower=0.0)
        print("lower = 0.0")
        return

    # Brauen
    if low == "a":
        set_group("brows", 1.0)
        return
    if low == "s":
        set_group("brows", 0.0)
        return

    if low == "0":
        set_all_neutral()
        return
    if low == "?":
        print(HELP)
        return
    if low == "x":
        raise KeyboardInterrupt

    print("Unbekanntes Kommando. '?' für Hilfe.")

# ------------------ INIT & MAIN ------------------

def init() -> bool:
    """Startet (idempotent) die WS-Verbindung - kompatibel zur BT-Version."""
    if not STATE._ws_started:
        threading.Thread(target=ws_worker, daemon=True).start()
        threading.Thread(target=sender_worker, daemon=True).start()
        STATE._ws_started = True
    return True

def main():
    print("Verbinde zu", WS_URL, "…")
    init()
    print(HELP)
    try:
        while True:
            inp = input("Key: ")
            process_command(inp)
            time.sleep(0.1)
    except (KeyboardInterrupt, EOFError):
        pass
    finally:
        STATE.stop_evt.set()
        time.sleep(0.2)
        print("Bye.")

if __name__ == "__main__":
    main()
