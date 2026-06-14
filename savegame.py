"""Speicherstand-Verwaltung für laufende Runs (mit Versionsprüfung)"""

import json
import os
from constants import SAVE_FILE, GAME_VERSION
import paths


def _path():
    return paths.data_path(SAVE_FILE)


def has_save():
    """True, wenn überhaupt eine Speicherdatei existiert"""
    return os.path.exists(_path())


def load_save():
    """
    Lädt den Speicherstand als Dict.
    Gibt None NUR zurück, wenn keine Datei da oder sie wirklich korrupt ist.

    WICHTIG: Spielstände werden NIE wegen der Version verworfen (Wunsch des
    Users: "Saves müssen IMMER gültig bleiben, egal was passiert"). Neue
    Save-Felder werden additiv mit Defaults hinzugefügt, und die
    Deserialisierung in game.py liest jedes Feld defensiv per .get(...).
    """
    if not os.path.exists(_path()):
        return None
    try:
        with open(_path(), "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError, ValueError):
        return None
    if not isinstance(data, dict):
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
        with open(_path(), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except OSError:
        return False


def delete_save():
    """Löscht den Speicherstand (z.B. bei Tod, Sieg oder neuem Run)"""
    try:
        if os.path.exists(_path()):
            os.remove(_path())
    except OSError:
        pass
