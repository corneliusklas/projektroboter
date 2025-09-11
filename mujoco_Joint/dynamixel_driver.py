"""
dynamixel_driver.py
===================

Ein Modul für Cable-Robot-Joint-Kalibrierung *und* Dynamixel-Steuerung.
───────────────────────────────────────────────────────────────────────
  • Liest Rohdaten aus calibration.cfg
  • Rechnet Modell- zu Motor-Werten (und zurück)
  • Kapselt PyPot-Funktionen: init(), set_joint_positions(), get_joint_positions()

Schema-Formel
-------------
    factor  = (robot0 - robot45) / (model0 - model45)
    motor   = (model - model0)   * factor + robot0
"""


from __future__ import annotations
import configparser
from pathlib import Path
from turtle import pos
from typing import Dict, Iterable

# ---------------- Servo-spezifische Konstanten ----------------
# Für AX-12A (0-1023 ↔ 0-300°)
REG_CENTER   = 512.0           # Registerwert für 0°
REG_PER_DEG  = 1023.0 / 300.0  # ≈ 3.410   Counts pro Grad
DEG_PER_REG  = 300.0  / 1023.0 # ≈ 0.2933  Grad  pro Count

# ---------------------- CFG laden ------------------------------------
_CFG_FILE = Path(__file__).with_name("calibration.cfg")
_cfg = configparser.ConfigParser()
_cfg.read(_CFG_FILE, encoding="utf-8")

# ---------------------- Hilfsfunktionen ------------------------------
def _sec(joint: str) -> configparser.SectionProxy:
    if joint not in _cfg:
        raise KeyError(f"Joint '{joint}' nicht in {_CFG_FILE.name} gefunden.")
    return _cfg[joint]

def factor(joint: str) -> float:
    s = _sec(joint)
    return (float(s["robot0"]) - float(s["robot45"])) / (float(s["model0"]) - float(s["model45"]))

def model2motor(joint: str, model_val: float) -> float:
    s = _sec(joint)
    reg_val = (model_val - float(s["model0"])) * factor(joint) + float(s["robot0"])
    return reg_val * REG_TO_DEG 

def motor2model(joint: str, motor_deg: float) -> float:
    reg_val = motor_deg * DEG_TO_REG
    s = _sec(joint)
    return (reg_val - float(s["robot0"])) / factor(joint) + float(s["model0"])

def motor_id(joint: str) -> int:
    return int(_sec(joint)["motor_id"])

def joint_name(motor_id_: int) -> str | None:
    for j, s in _cfg.items():
        if s.get("motor_id") and int(s["motor_id"]) == motor_id_:
            return j
    return None

# ---------------------- Dynamixel-Layer ------------------------------
_DXL = None           # wird von init() gesetzt
_MOVE_ENABLED = False

def init(port: str = "COM17", baudrate: int = 1_000_000) -> None:
    """Öffnet den Dynamixel-Port und schaltet Torque ein."""
    global _DXL, _MOVE_ENABLED
    try:
        from pypot.dynamixel import DxlIO
    except ImportError as e:
        raise RuntimeError("PyPot nicht installiert (`pip install pypot`)") from e

    _DXL = DxlIO(port, baudrate=baudrate)
    ids = [int(s["motor_id"]) for s in _cfg.values() if "motor_id" in s]
    _DXL.enable_torque(ids)
    _DXL.set_max_torque({i: 1023 for i in ids})
    _MOVE_ENABLED = True
    print(f"[dynamixel_driver] Verbunden mit {port}, IDs: {ids}")

def set_joint_positions(model_q: Dict[str, float]) -> None:
    """
    Nimmt ein Dict {joint_name: model_val} und sendet
    die entsprechenden Dynamixel-Positionen.
    """
    goal = {motor_id(j): model2motor(j, q) for j, q in model_q.items()}
    print(f"[dynamixel_driver] Setze Positionen: {goal}")
    if not _MOVE_ENABLED:
        print("[dynamixel_driver] MOVE nicht aktiviert, init() aufrufen.")
        return
    if goal:
        _DXL.set_goal_position(goal) #grad


def get_joint_positions(joints: Iterable[str]) -> Dict[str, float]:
    """
    Liest aktuelle Dynamixel-Positionen dieser Joints zurück
    und wandelt sie in Modell-Einheiten.
    """
    ids = [motor_id(j) for j in joints]
    pos = _DXL.get_present_position(ids)  # Motor-Positionen in Grad
    return {joint_name(i): motor2model(joint_name(i), v) for i, v in zip(ids, pos)}
    #return {joint_name(i): {joint_name(i), v} for i, v in zip(ids, pos)}

# ---------------------- Mini-Demo ------------------------------------
if __name__ == "__main__":
    #print("Factor Eb1_x:", factor("Eb1_x"))
    # Hardware-Teil nur ausführen, wenn Port existiert
    #init(); 
    #print all motor positions
    #pos=get_joint_positions(_cfg.sections())
    #print("Current motor positions, but wrong:", pos)

    #set_joint_positions({'Eb1_x': 0.25})
    #pos= input("enter postion in motor units: ")
    #set_joint_positions({'Rotation': int(pos)})
    set_joint_positions({'Rotation': 0})
    set_joint_positions({'Sh_x': 0.046})

    #index=3
    #for i in range(5):
    #    pos= input("enter postion in motor units: ")
    #    _DXL.set_goal_position({index: pos})
