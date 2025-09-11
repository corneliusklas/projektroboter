#!/usr/bin/env python3
# slider_player.py
# -------------------------------------------------------------
# Dynamixel-Slider-GUI mit Keyframe-Recorder + JSON-Editor
# © 2025  (Public Domain / MIT)
# -------------------------------------------------------------

import json, time, threading, tkinter as tk
import tkinter.ttk as ttk
import tkinter.simpledialog as sd
import tkinter.filedialog as fd
from pathlib import Path

# -------------------------------------------------------------------
#  Dynamixel-Setup
# -------------------------------------------------------------------
MOVE      = True            # False: reine Simulation (kein USB nötig)
DXL_PORT  = "COM17"
BAUDRATE  = 1_000_000

#fixed ID List
ids  = [4,3,5,6,12,16,15,13,10,18]
names = ["Rotation", "Sh_x", "Sh_y", "El1_x", "El1_y", "El2_x", "El2_y", "Wrist_x", "Wrist_y", "Gripper"]
moving_speed ={mid: 1023 for mid in ids}
TORQUE_HIGH = 100
TORQUE_LOW  = 0
torque_limit = {mid: TORQUE_HIGH for mid in ids}
#goal_position = {mid: 0 for mid in ids}
try:
    if MOVE:
        from pypot.dynamixel import DxlIO
        io  = DxlIO(DXL_PORT, baudrate=BAUDRATE)
        #ids = io.get_id_list()
        io.enable_torque(ids)
        #check if all ids are enabled
        #for mid in ids: 
         #   if not io.is_torque_enabled(mid):
        #        raise RuntimeError(f"Torque für ID {mid} nicht aktiviert!")
    else:
        raise RuntimeError
except Exception as e:
    print(f"[Error] {e}")
    print("[Info] Starte im Sim-Modus (MOVE=False)")
    MOVE = False
    #ids  = [3,4,5,6,13,14,15,16,17,18]      # Demo-IDs


# -------------------------------------------------------------------
#  Tk-GUI Grundaufbau
# -------------------------------------------------------------------
root = tk.Tk(); root.title("Dynamixel Slider Player")

left  = ttk.Frame(root, padding=10)
right = ttk.Frame(root, padding=10)
left.grid (row=0, column=0, sticky="ns")
right.grid(row=0, column=1, sticky="nsew")
root.columnconfigure(1, weight=1); root.rowconfigure(0, weight=1)

# ---- Slider links ---------------------------------------------------
slider = {}
for r, mid in enumerate(ids):
    name = names[r]
    ttk.Label(left, text=f"{name} (ID {mid})").grid(row=r, column=0, sticky="e")
    s = ttk.Scale(left, from_=-150, to=150, length=250, orient="horizontal")
    s.grid(row=r, column=1, padx=5, pady=2)
    slider[mid] = s

#button um die motoren an und auszuschalten
def toggle_torque():
    global  torque_limit
    if torque_limit == {mid: TORQUE_LOW for mid in ids}:
            torque_limit = {mid: TORQUE_HIGH for mid in ids}
            status("⚠ Torque High")
    else:
    #io.enable_torque(ids)
        torque_limit = {mid: TORQUE_LOW for mid in ids}
        status("✔ Torque Low")

ttk.Button(left, text="Toggle Torque", command=toggle_torque).grid(row=len(ids), column=0, columnspan=2, pady=6)

#button um alle geschwindigkeiten auf volles Tempo zu setzen
def set_max_speed():
    global MOVE
    global moving_speed, torque_limit
    if MOVE:
        moving_speed ={mid: 1023 for mid in ids}
        status("✔ Maximalgeschwindigkeit gesetzt")
        #set torque to maximum
        torque_limit = {mid: TORQUE_HIGH for mid in ids}
    else:
        status("⚠ MOVE ist deaktiviert")
ttk.Button(left, text="Set Max Speed", command=set_max_speed).grid(row=len(ids)+1, column=0, columnspan=2, pady=6)

#button und eingabefeld  um die complience slope für alle motoren zu setzen
def set_compliance_slope():
    global MOVE
    if MOVE:
        slope = sd.askfloat("Compliance Slope", "Geben Sie den Wert für die Compliance Slope ein (0-255):",
                            minvalue=0, maxvalue=255)
        if slope is not None:

            for id in ids:
                io.set_compliance_slope(id, int(slope))

            status(f"✔ Compliance Slope auf {slope} gesetzt. (Falls Kommando angekommen)")
    else:
        status("⚠ MOVE ist deaktiviert")

ttk.Button(left, text="Set Compliance Slope", command=set_compliance_slope).grid(row=len(ids)+2, column=0, columnspan=2, pady=6)

# ---- JSON-Editor rechts --------------------------------------------
right.columnconfigure(0, weight=1); right.rowconfigure(1, weight=1)

ttk.Label(right, text="Keyframe-JSON").grid(row=0, column=0, sticky="w")
text = tk.Text(right, wrap="none", width=50, height=28)
text.grid(row=1, column=0, sticky="nsew")
scroll = ttk.Scrollbar(right, orient="vertical", command=text.yview)
scroll.grid(row=1, column=1, sticky="ns")
text.configure(yscrollcommand=scroll.set)

# ---- Button-Leiste --------------------------------------------------
btn_bar = ttk.Frame(right); btn_bar.grid(row=2, column=0, columnspan=2, pady=6)
for i in range(5): btn_bar.columnconfigure(i, weight=1)

# ---- Datenhaltung ---------------------------------------------------
keyframes: list[dict] = []
current_file = Path("keyframes.json")

def refresh_editor() -> None:
    text.delete("1.0", "end")
    text.insert("1.0", json.dumps(keyframes, indent=2))

def status(msg: str) -> None:
    status_lbl["text"] = msg

# ---- Datei-Funktionen ----------------------------------------------
def load_file(path: str | None = None):
    global keyframes, current_file
    if path is None:
        path = fd.askopenfilename(defaultextension=".json",
                                  filetypes=[("JSON-Datei", "*.json")])
        if not path: return
    current_file = Path(path)
    try:
        keyframes = json.loads(current_file.read_text())
        refresh_editor(); status(f"✔  geladen: {current_file.name}")
    except Exception as e:
        status(f"⚠ Ladefehler: {e}")

def save_file(path: str | None = None):
    global current_file
    if path is None:
        path = current_file
    else:
        current_file = Path(path)
    try:
        # Editor-Inhalt validieren
        keyframes[:] = json.loads(text.get("1.0", "end"))
        current_file.write_text(json.dumps(keyframes, indent=2))
        status(f"💾 gespeichert: {current_file.name}")
    except Exception as e:
        status(f"⚠ Speicherfehler: {e}")

# ---- Keyframe-Handling ---------------------------------------------
def save_keyframe():
    dur = sd.askfloat("Zeit (s)", "Zeit bis zum nächsten Frame:",
                      minvalue=0.05, maxvalue=30.0)
    if dur is None: return
    entry = {
        "time": dur,
        "pos": {mid: s.get() for mid, s in slider.items()}
    }
    keyframes.append(entry); refresh_editor()
    status(f"➕ Keyframe (t={dur:.2f}s)")

def clear_keys():
    keyframes.clear(); refresh_editor()
    status("Liste geleert")

MAX_SPEED = 150.0  # Begrenzung (°/s)

def playback():
    if not keyframes:
        status("⚠ Keine Keyframes"); return
    prev = {mid: slider[mid].get() for mid in ids}
    status("▶ Playback …")

    for kf in keyframes:
        t = kf["time"]
        # Tempo pro Motor berechnen
        speed = {}
        for mid in ids:
            delta = abs(kf["pos"].get(mid, prev[mid]) - prev[mid])
            if delta > 0.1:  # nur wenn Bewegung nötig
                speed[mid] = min(MAX_SPEED, max(0, delta / max(.01, t)))

        # -> Hardware
        if MOVE:
            global moving_speed, goal_position, torque_limit
            moving_speed= speed
            print (f"Setze Geschwindigkeiten: {speed}")
            #goal_position=(kf["pos"]) -> über slider

        # Slider synchronisieren
        for mid, deg in kf["pos"].items():
            slider[mid].set(deg)
        prev = kf["pos"]
        time.sleep(t)

    
    if MOVE:
        #at the end of playback
        #set all speeds to full speed
        moving_speed={mid: 1023 for mid in ids}
        #set torque to full torque
        torque_limit={mid: 100 for mid in ids}
    status("■ Playback fertig")

# ---- Buttons verknüpfen --------------------------------------------
ttk.Button(btn_bar, text="Save key", command=save_keyframe)\
      .grid(row=0, column=0, sticky="ew", padx=2)
ttk.Button(btn_bar, text="▶ Play",
           command=lambda: threading.Thread(target=playback, daemon=True).start())\
      .grid(row=0, column=1, sticky="ew", padx=2)
ttk.Button(btn_bar, text="⟳ Clear", command=clear_keys)\
      .grid(row=0, column=2, sticky="ew", padx=2)
ttk.Button(btn_bar, text="💾 Save as …",
           command=lambda: save_file(fd.asksaveasfilename(
               defaultextension=".json", filetypes=[("JSON", "*.json")])))\
      .grid(row=0, column=3, sticky="ew", padx=2)
ttk.Button(btn_bar, text="📂 Load …", command=lambda: load_file())\
      .grid(row=0, column=4, sticky="ew", padx=2)
#button um die text einträge ins programm zu übernehmen
def apply_text():
    global keyframes
    try:
        raw = json.loads(text.get("1.0", "end"))
        for kf in raw:
                    kf["pos"] = {int(mid): v for mid, v in kf["pos"].items()}
        keyframes = raw

        refresh_editor()
        status("✔ Text übernommen")
    except json.JSONDecodeError as e:
        status(f"⚠ JSON-Fehler: {e}")
ttk.Button(right, text="Apply Text", command=apply_text)\
      .grid(row=3, column=0, columnspan=2, pady=6)




# ---- Statusleiste ---------------------------------------------------
status_lbl = ttk.Label(root, text="Bereit.", relief="sunken", anchor="w")
status_lbl.grid(row=1, column=0, columnspan=2, sticky="ew")

# Lade Default-Datei, falls vorhanden
if current_file.exists():
    try:
        keyframes = json.loads(current_file.read_text())
        refresh_editor()
        status(f"✔  {current_file.name} geladen")
    except Exception:
        status("⚠  Default-JSON konnte nicht geladen werden")


# ---- Temperatur-Anzeige ---------------------------------------------------
temp_frame = ttk.Frame(right)
temp_frame.grid(row=4, column=0, columnspan=2, sticky="ew", pady=6)
ttk.Label(temp_frame, text="Motor-Temperaturen:").grid(row=0, column=0, sticky="w")
temp_vars = {mid: tk.StringVar(value="--- °C") for mid in ids}
for i, mid in enumerate(ids):
    ttk.Label(temp_frame, text=f"ID {mid}:").grid(row=1, column=i*2, sticky="e")
    ttk.Label(temp_frame, textvariable=temp_vars[mid]).grid(row=1, column=i*2+1, sticky="w")

def update_temps():
    if MOVE:
        try:
            temps = io.get_present_temperature(ids)
            for mid, temp in zip(ids, temps):
                temp_vars[mid].set(f"{temp} °C")
        except Exception as e:
            for mid in ids:
                temp_vars[mid].set("Fehler")
    else:
        for mid in ids:
            temp_vars[mid].set("--- °C")
    root.after(1000, update_temps)  # alle 1s aktualisieren

# ---- Permanenter TX-Thread (Slider → Motor) ------------------------
def tx_loop():
    global MOVE, moving_speed, torque_limit
    while True:
        if MOVE:
            io.set_goal_position({mid: s.get() for mid, s in slider.items()})
            io.set_moving_speed(moving_speed)
            io.set_torque_limit(torque_limit)
            #print(f"Setze torques: {torque_limit}")
        time.sleep(0.01) # 0.05->20 Hz


threading.Thread(target=tx_loop, daemon=True).start()

update_temps()

root.mainloop()
