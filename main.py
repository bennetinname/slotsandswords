"""
SLOTS & SWORDS: Ein Roguelike-Kartenspiel-Spielautomat
"Slay the Spire trifft Balatro trifft einen Spielautomaten in einer dubiosen Bahnhofskneipe"

Starte mit: python main.py
"""

import pygame
import sys
from game import Game
from constants import GAME_VERSION
import audio
import options as _opts

def main():
    pygame.init()
    pygame.display.set_caption(f"Slots & Swords  v{GAME_VERSION}")

    # Gespeicherte Optionen lesen, damit das erste Fenster die richtige Größe hat
    saved = _opts.load()
    if saved.get("fullscreen"):
        info = pygame.display.Info()
        screen = pygame.display.set_mode(
            (info.current_w, info.current_h), pygame.FULLSCREEN)
    else:
        w = saved.get("window_w", 1280)
        h = saved.get("window_h", 720)
        screen = pygame.display.set_mode((w, h), pygame.RESIZABLE)

    clock = pygame.time.Clock()

    # Audio initialisieren (prozedural, still bei fehlendem Audiogerät)
    audio.init()
    audio.start_music()

    game = Game(screen, clock)
    game.run()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
