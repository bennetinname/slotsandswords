"""Lifetime-Statistiken über alle Runs (JSON via paths)."""

import json

import paths

STATS_FILE = "stats.json"


def _path():
    return paths.data_path(STATS_FILE)


def load():
    try:
        with open(_path(), "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def report_run(floor, kills, gold_earned):
    """Aktualisiert die Lifetime-Stats nach einem Run. Gibt das neue Dict zurück."""
    s = load()
    s["runs_played"] = s.get("runs_played", 0) + 1
    s["best_floor"] = max(s.get("best_floor", 0), floor)
    s["total_kills"] = s.get("total_kills", 0) + kills
    s["total_gold"] = s.get("total_gold", 0) + gold_earned
    try:
        with open(_path(), "w", encoding="utf-8") as f:
            json.dump(s, f, indent=2)
    except Exception:
        pass
    return s
