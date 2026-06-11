"""Stabiler Speicherort für Laufzeitdaten (Highscores, Save, Optionen).

WICHTIG: In einer PyInstaller-One-File-EXE zeigt __file__ in einen temporären
Ordner (_MEIxxxx), der beim Beenden gelöscht wird. Dort gespeicherte Dateien
wären nach einem Neustart weg. Deshalb schreiben wir NEBEN die EXE bzw. neben
die Skripte.
"""

import os
import sys


def data_dir():
    if getattr(sys, "frozen", False):          # gebündelte EXE
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def data_path(name):
    return os.path.join(data_dir(), name)
