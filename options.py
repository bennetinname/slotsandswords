"""Persistente Spieloptionen (Lautstärke, Anzeige) in options.json."""

import json
import paths

OPTIONS_FILE = "options.json"


def _path():
    return paths.data_path(OPTIONS_FILE)

DEFAULTS = {
    "master": 0.8,      # Gesamtlautstärke 0..1
    "music": 0.5,       # Musik 0..1
    "sfx": 0.6,         # Soundeffekte 0..1
    "fullscreen": False,
    "shake": True,      # Screen-Shake an/aus
    "particles": True,  # Partikeleffekte an/aus
    "fast": False,      # Animationen/Übergänge beschleunigen
    "window_w": 1280,   # Fenstergröße (Breite), nur im Fenstermodus
    "window_h": 720,    # Fenstergröße (Höhe)
    "last_seen": "",    # zuletzt gesehene Version (für Changelog-Auto-Popup)
}

# Vordefinierte Fenstergrößen (Name, Breite, Höhe)
WINDOW_PRESETS = [
    ("960×540",   960,  540),
    ("1280×720",  1280, 720),
    ("1600×900",  1600, 900),
    ("1920×1080", 1920, 1080),
]

_FLOATS = ("master", "music", "sfx")
_BOOLS = ("fullscreen", "shake", "particles", "fast")
_INTS = ("window_w", "window_h")


def load():
    o = dict(DEFAULTS)
    try:
        with open(_path(), "r", encoding="utf-8") as f:
            d = json.load(f)
        if isinstance(d, dict):
            for k in DEFAULTS:
                if k in d:
                    o[k] = d[k]
    except (OSError, json.JSONDecodeError, ValueError):
        pass
    # Sanitäts-Check
    for k in _FLOATS:
        try:
            o[k] = min(1.0, max(0.0, float(o[k])))
        except (TypeError, ValueError):
            o[k] = DEFAULTS[k]
    for k in _BOOLS:
        o[k] = bool(o[k])
    for k in _INTS:
        try:
            o[k] = int(o[k])
        except (TypeError, ValueError):
            o[k] = DEFAULTS[k]
    # Mindestgröße
    o["window_w"] = max(640, o["window_w"])
    o["window_h"] = max(480, o["window_h"])
    return o


def save(o):
    try:
        with open(_path(), "w", encoding="utf-8") as f:
            json.dump({k: o.get(k, DEFAULTS[k]) for k in DEFAULTS}, f, indent=2)
    except OSError:
        pass
