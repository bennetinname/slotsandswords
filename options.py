"""Persistente Spieloptionen (Lautstärke, Anzeige) in options.json."""

import json
import os

OPTIONS_FILE = "options.json"

DEFAULTS = {
    "master": 0.8,      # Gesamtlautstärke 0..1
    "music": 0.5,       # Musik 0..1
    "sfx": 0.6,         # Soundeffekte 0..1
    "fullscreen": False,
    "shake": True,      # Screen-Shake an/aus
    "particles": True,  # Partikeleffekte an/aus
}

_FLOATS = ("master", "music", "sfx")
_BOOLS = ("fullscreen", "shake", "particles")


def load():
    o = dict(DEFAULTS)
    try:
        with open(OPTIONS_FILE, "r", encoding="utf-8") as f:
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
    return o


def save(o):
    try:
        with open(OPTIONS_FILE, "w", encoding="utf-8") as f:
            json.dump({k: o.get(k, DEFAULTS[k]) for k in DEFAULTS}, f, indent=2)
    except OSError:
        pass
