"""
Asset-Lade-Schicht mit Cache + Procedural-Fallback.
Fehlt eine Datei, gibt die Funktion None zurück -> der Aufrufer zeichnet
dann wie bisher prozedural. So kann man Sprites risikofrei nachrüsten.
Funktioniert aus dem Quellordner UND aus der PyInstaller-One-File-EXE.
"""

import os
import sys
import pygame

_surf_cache = {}     # (cat,name) -> Surface | None
_scaled_cache = {}   # (cat,name,w,h) -> Surface


def _base_dir():
    if getattr(sys, "frozen", False):            # PyInstaller-EXE
        return os.path.join(getattr(sys, "_MEIPASS", os.path.dirname(sys.executable)), "assets")
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


BASE = _base_dir()


def load(cat, name):
    """Lädt ein Sprite (gecacht). Gibt None zurück, wenn nicht vorhanden."""
    if name is None:
        return None
    key = (cat, name)
    if key in _surf_cache:
        return _surf_cache[key]
    path = os.path.join(BASE, cat, str(name) + ".png")
    surf = None
    if os.path.exists(path):
        try:
            img = pygame.image.load(path)
            surf = img.convert_alpha() if pygame.display.get_init() and pygame.display.get_surface() else img
        except Exception:
            surf = None
    _surf_cache[key] = surf
    return surf


def has(cat, name):
    return load(cat, name) is not None


def scaled(cat, name, w, h):
    """Auf exakte Größe skaliert (gecacht). None wenn nicht vorhanden."""
    base = load(cat, name)
    if base is None:
        return None
    w, h = int(w), int(h)
    key = (cat, name, w, h)
    s = _scaled_cache.get(key)
    if s is None:
        s = pygame.transform.smoothscale(base, (max(1, w), max(1, h)))
        _scaled_cache[key] = s
    return s


def fit(cat, name, max_w, max_h):
    """Skaliert proportional in eine Box (max_w x max_h). None wenn nicht vorhanden."""
    base = load(cat, name)
    if base is None:
        return None
    bw, bh = base.get_size()
    sc = min(max_w / bw, max_h / bh)
    return scaled(cat, name, round(bw * sc), round(bh * sc))


def by_height(cat, name, h):
    """Skaliert auf eine Zielhöhe (Breite proportional). None wenn nicht vorhanden."""
    base = load(cat, name)
    if base is None:
        return None
    bw, bh = base.get_size()
    return scaled(cat, name, round(bw * h / bh), h)
