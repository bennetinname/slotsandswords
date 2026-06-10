"""
SLOTS & SWORDS: Ein Roguelike-Kartenspiel-Spielautomat
"Slay the Spire trifft Balatro trifft einen Spielautomaten in einer dubiosen Bahnhofskneipe"

Starte mit: python main.py
"""

import pygame
import sys
from game import Game
import audio

def main():
    pygame.init()
    pygame.display.set_caption("Slots & Swords")

    screen = pygame.display.set_mode((1200, 800))
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
