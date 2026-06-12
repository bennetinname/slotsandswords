"""
Tages-Challenge: fester Seed + Modifikator pro Kalendertag, eigene Tagesbestwertung
und Spiel-Streak (an wie vielen Tagen in Folge gespielt). JSON via paths.
"""

import json
import datetime

import paths

DAILY_FILE = "daily.json"

# Modifikatoren des Tages (deterministisch über das Datum gewählt)
MODIFIERS = [
    {"id": "goldrush",  "name": "Goldrausch",
     "desc": "+50% Gold von Gegnern, aber Gegner haben +20% HP.",
     "gold_mult": 1.5, "enemy_hp_mult": 1.2, "enemy_dmg_mult": 1.0},
    {"id": "glass",     "name": "Glasknochen",
     "desc": "Du startest mit 70 Max HP, dafür +1 Energie pro Runde.",
     "max_hp": 70, "bonus_energy": 1},
    {"id": "horde",     "name": "Die Horde",
     "desc": "Gegner schlagen +25% härter, geben aber +40% Gold.",
     "enemy_dmg_mult": 1.25, "gold_mult": 1.4},
    {"id": "lucky_day", "name": "Glückstag",
     "desc": "Jeder Kampf startet mit +1 Glücksrunde. Gegner +15% HP.",
     "start_lucky": 1, "enemy_hp_mult": 1.15},
    {"id": "toxic",     "name": "Giftiger Boden",
     "desc": "ALLE Gegner starten mit 4 Gift. Deine Heilung ist halbiert.",
     "enemy_start_poison": 4, "heal_mult": 0.5},
    {"id": "high_roller", "name": "High Roller",
     "desc": "Start mit 150 Gold, aber Gegner haben +30% HP.",
     "start_gold": 150, "enemy_hp_mult": 1.3},
    {"id": "berserk",   "name": "Berserker-Tag",
     "desc": "+3 Stärke ab Start, aber 80 Max HP.",
     "start_strength": 3, "max_hp": 80},
]


def today_key():
    return datetime.date.today().isoformat()


def seed_for_today():
    """Deterministischer Seed: alle Spieler bekommen heute dieselbe Map."""
    d = datetime.date.today()
    return d.year * 10000 + d.month * 100 + d.day


def modifier_for_today():
    return MODIFIERS[seed_for_today() % len(MODIFIERS)]


def _path():
    return paths.data_path(DAILY_FILE)


def _load():
    try:
        with open(_path(), "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save(data):
    try:
        with open(_path(), "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass


def get_today_best():
    """Beste heutige Punktzahl (0 wenn heute noch nicht gespielt)."""
    d = _load()
    if d.get("date") == today_key():
        return d.get("best", 0)
    return 0


def get_streak():
    """Aktuelle Tages-Streak (heute zählt mit, wenn heute gespielt)."""
    return _load().get("streak", 0)


def report_run(score):
    """Meldet einen beendeten Tages-Run. Gibt (neuer_bestwert, streak) zurück."""
    d = _load()
    today = today_key()
    yesterday = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()

    if d.get("date") == today:
        streak = d.get("streak", 1)
        best = max(d.get("best", 0), score)
        new_best = score > d.get("best", 0)
    else:
        streak = d.get("streak", 0) + 1 if d.get("date") == yesterday else 1
        best = score
        new_best = True

    _save({"date": today, "best": best, "streak": streak})
    return new_best, streak
