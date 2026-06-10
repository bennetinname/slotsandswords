"""Highscore-System: Speichert und lädt Bestenliste als JSON"""

import json
import os
from datetime import datetime
from constants import HIGHSCORE_FILE, MAX_HIGHSCORES


def _score_path():
    """Pfad zur Highscore-Datei (neben den Spieldateien)"""
    base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, HIGHSCORE_FILE)


def load_highscores():
    """Lädt die Highscore-Liste. Gibt leere Liste zurück falls keine Datei existiert."""
    path = _score_path()
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
        return []
    except (json.JSONDecodeError, OSError):
        # Beschädigte Datei: ignorieren statt crashen
        return []


def calculate_score(player, floor_num, won=False):
    """
    Berechnet den Punktestand aus dem Spielzustand.
    Etage zählt am meisten, dazu Boni für Gold, Schaden, Hühner.
    """
    score = 0
    score += floor_num * 1000               # Fortschritt ist König
    score += player.gold_earned * 2          # Verdientes Gold
    score += player.damage_dealt             # Verursachter Schaden
    score += player.chickens_summoned * 50   # Hühner sind wertvoll
    score += player.enemies_defeated * 200   # Siege
    if won:
        score += 10000                       # Sieg-Bonus
    return int(score)


def add_highscore(player, floor_num, won=False):
    """
    Fügt einen neuen Eintrag hinzu, sortiert und schneidet auf MAX_HIGHSCORES.
    Gibt (rang, score, ist_neuer_rekord) zurück. rang ist None falls nicht platziert.
    """
    score = calculate_score(player, floor_num, won)
    scores = load_highscores()
    
    entry = {
        "score": score,
        "floor": floor_num,
        "gold": player.gold_earned,
        "chickens": player.chickens_summoned,
        "won": won,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    
    scores.append(entry)
    scores.sort(key=lambda e: e.get("score", 0), reverse=True)
    
    # Rang des neuen Eintrags ermitteln (vor dem Abschneiden)
    rank = None
    for i, e in enumerate(scores):
        if e is entry:
            rank = i + 1
            break
    
    is_record = (rank == 1)
    scores = scores[:MAX_HIGHSCORES]
    
    # Nur platzierte Einträge werden gespeichert
    placed = entry in scores
    
    try:
        with open(_score_path(), "w", encoding="utf-8") as f:
            json.dump(scores, f, indent=2, ensure_ascii=False)
    except OSError:
        pass  # Schreibfehler nicht spielentscheidend
    
    return (rank if placed else None, score, is_record)
