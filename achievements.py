"""
Erfolge (Achievements) – dauerhaft über Runs hinweg, JSON-Persistenz via paths.
Freischalt-Logik liegt in game.py (ruft unlock(id) an den Trigger-Punkten auf).
"""

import json
import time

import paths

ACHIEVEMENT_FILE = "achievements.json"

# Reihenfolge = Anzeige-Reihenfolge im Erfolge-Screen
DEFS = [
    {"id": "first_blood",    "emoji": "🗡️", "name": "Erstes Blut",
     "desc": "Besiege deinen ersten Gegner."},
    {"id": "boss_kill",      "emoji": "👑", "name": "Königsmörder",
     "desc": "Besiege einen Boss."},
    {"id": "elite_kill",     "emoji": "⭐", "name": "Elitejäger",
     "desc": "Besiege einen Elite-Gegner."},
    {"id": "act1",           "emoji": "🚪", "name": "Akt eins steht",
     "desc": "Schließe Akt 1 ab."},
    {"id": "act3",           "emoji": "🏰", "name": "Tiefer Lauf",
     "desc": "Schließe Akt 3 ab."},
    {"id": "marathon",       "emoji": "🏃", "name": "Marathon",
     "desc": "Erreiche Etage 20 in einem Run."},
    {"id": "triple",         "emoji": "🎰", "name": "Drilling!",
     "desc": "Lande drei gleiche Symbole im Slot."},
    {"id": "gamble_jackpot", "emoji": "💰", "name": "Hausverbot",
     "desc": "Knacke den Jackpot am Glücksrad im Shop."},
    {"id": "combo_5",        "emoji": "🔥", "name": "Kombo-Künstler",
     "desc": "Erreiche eine 5er-Kombo in einem Kampf."},
    {"id": "rich",           "emoji": "🪙", "name": "Goldesel",
     "desc": "Besitze 300 Gold auf einmal."},
    {"id": "muscles",        "emoji": "💪", "name": "Muskelpaket",
     "desc": "Erreiche 10 Stärke in einem Run."},
    {"id": "near_death",     "emoji": "💀", "name": "Dem Tod von der Schippe",
     "desc": "Überlebe einen Gegnerzug mit genau 1 HP."},
    {"id": "flawless_boss",  "emoji": "✨", "name": "Makellos",
     "desc": "Besiege einen Boss mit vollen HP."},
    {"id": "relic_5",        "emoji": "💠", "name": "Sammler",
     "desc": "Trage 5 Relikte gleichzeitig."},
    {"id": "slim_deck",      "emoji": "🃏", "name": "Weniger ist mehr",
     "desc": "Besiege einen Boss mit höchstens 8 Karten im Deck."},
    {"id": "first_death",    "emoji": "🪦", "name": "Lehrgeld",
     "desc": "Stirb. Passiert den Besten."},
]

_DEF_BY_ID = {d["id"]: d for d in DEFS}
_unlocked = {}   # id -> Unix-Timestamp

# ─── Meta-Unlocks: Inhalte, die hinter Erfolgen stecken ───
# (kind, name) -> Erfolgs-ID. Gesperrte Inhalte tauchen nicht in
# Belohnungen/Shops auf, bis der Erfolg freigeschaltet ist.
UNLOCK_REWARDS = {
    ("card", "Säurefass"):    "triple",
    ("card", "Henkersbeil"):  "boss_kill",
    ("card", "Blutpakt"):     "near_death",
    ("card", "Stachelhaut"):  "elite_kill",
    ("relic", "Trophäensammlung"): "act1",
    ("relic", "Vampirzahn"):       "combo_5",
}


def content_unlocked(kind, name):
    """True, wenn die Karte/das Relikt verfügbar ist (kein Lock oder Erfolg geschafft)."""
    req = UNLOCK_REWARDS.get((kind, name))
    return req is None or req in _unlocked


def rewards_for(aid):
    """Liste der (kind, name), die dieser Erfolg freischaltet."""
    return [k for k, v in UNLOCK_REWARDS.items() if v == aid]


def _path():
    return paths.data_path(ACHIEVEMENT_FILE)


def load():
    """Lädt freigeschaltete Erfolge (still bei Fehlern)."""
    global _unlocked
    try:
        with open(_path(), "r", encoding="utf-8") as f:
            data = json.load(f)
        _unlocked = {k: v for k, v in data.get("unlocked", {}).items()
                     if k in _DEF_BY_ID}
    except Exception:
        _unlocked = {}


def _save():
    try:
        with open(_path(), "w", encoding="utf-8") as f:
            json.dump({"unlocked": _unlocked}, f, indent=2)
    except Exception:
        pass


def unlock(aid):
    """Schaltet einen Erfolg frei. True, wenn er NEU ist (für Toast)."""
    if aid not in _DEF_BY_ID or aid in _unlocked:
        return False
    _unlocked[aid] = int(time.time())
    _save()
    return True


def is_unlocked(aid):
    return aid in _unlocked


def get(aid):
    return _DEF_BY_ID.get(aid)


def progress():
    """(freigeschaltet, gesamt)"""
    return len(_unlocked), len(DEFS)
