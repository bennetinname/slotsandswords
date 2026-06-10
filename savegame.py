"""Speicherstand-Verwaltung für laufende Runs (mit Versionsprüfung)"""

import json
import os
from constants import SAVE_FILE, GAME_VERSION


def has_save():
    """True, wenn überhaupt eine Speicherdatei existiert"""
    return os.path.exists(SAVE_FILE)


def load_save():
    """
    Lädt den Speicherstand als Dict.
    Gibt None zurück, wenn keine Datei da, sie korrupt oder die
    Version inkompatibel ist (Save-Versionierung).
    """
    if not os.path.exists(SAVE_FILE):
        return None
    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError, ValueError):
        return None
    if not isinstance(data, dict):
        return None
    if data.get("version") != GAME_VERSION:
        # Stand stammt aus einer anderen Spielversion -> nicht laden
        return None
    return data


def has_valid_save():
    """True, wenn ein ladbarer, versionskompatibler Stand existiert"""
    return load_save() is not None


def write_save(data):
    """Schreibt den Spielstand und stempelt die aktuelle Version ein"""
    data = dict(data)
    data["version"] = GAME_VERSION
    try:
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except OSError:
        return False


def delete_save():
    """Löscht den Speicherstand (z.B. bei Tod, Sieg oder neuem Run)"""
    try:
        if os.path.exists(SAVE_FILE):
            os.remove(SAVE_FILE)
    except OSError:
        pass
