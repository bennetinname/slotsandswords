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
    "difficulty": 1,    # 0=Einfach, 1=Normal, 2=Hart (skaliert Gegner)
    "last_seen": "",    # zuletzt gesehene Version (für Changelog-Auto-Popup)
}

# Gegner-Skalierung je Schwierigkeit: (hp_mult, dmg_mult)
DIFFICULTY = [
    ("Einfach", 0.80, 0.80),
    ("Normal",  1.00, 1.00),
    ("Hart",    1.25, 1.20),
]

_FLOATS = ("master", "music", "sfx")
_BOOLS = ("fullscreen", "shake", "particles", "fast")
_INTS = ("difficulty",)


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
    o["difficulty"] = min(2, max(0, o["difficulty"]))
    return o


def save(o):
    try:
        with open(_path(), "w", encoding="utf-8") as f:
            json.dump({k: o.get(k, DEFAULTS[k]) for k in DEFAULTS}, f, indent=2)
    except OSError:
        pass
