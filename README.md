# 🎰⚔️ Slots & Swords

Ein **Roguelike-Kartenspiel-Spielautomat** im düster-humorvollen *Dive-Bar-Casino*-Stil.
Kämpfe dich über eine verzweigte Pfad-Karte nach oben, spiele Karten, **drehe den
Spielautomaten** und sammle Relikte – Akt für Akt, endlos und immer härter.

Geschrieben in **Python + pygame**.

> ### 🤖 100 % „vibe coded"
> Dieses Projekt ist **komplett vibe-coded** – als Test, *was geht*, wenn man ein
> ganzes Spiel rein durch Zuruf an eine KI entstehen lässt. Vom ersten Prototyp
> über UI, Audio, Pixel-Art-Integration, Balancing bis hin zum In-Game-Auto-Updater
> wurde (fast) jede Zeile per natürlicher Sprache beauftragt statt von Hand getippt.
> Es ist ein Experiment – entsprechend darf man Ecken & Kanten mit einem
> Augenzwinkern sehen. 😄

---

## 🎮 Worum geht's?

Jede Runde besteht aus zwei Phasen:

1. **Karten spielen** – Energie ausgeben, Schaden machen, blocken, Status verteilen.
2. **Slot drehen** – der Spielautomat entscheidet über Bonus-Schaden, Gold, Heilung
   und verrückte Kombos. Drei gleiche Symbole = Jackpot.

Danach schlägt der Gegner zurück. Überlebe, wähle deine Belohnung und zieh weiter.
Nach jedem **Boss** beginnt ein neuer, härterer **Akt**.

## ✨ Features

- **3 Start-Klassen** (Ritter / Hochstapler / Hexe) – je eigenes Deck & Start-Relikt
- **92 Karten**, **42 Relikte**, **37 Gegner**, **6 Akt-Themen** mit eigenen
  Gegner-Pools, Bossen und Hintergründen
- **Tiefes Statussystem**: Gift, Brennen, Frost, Verwundbar, Markiert, Betäubt,
  Verhängnis, Wut, Fokus, Dornen, Regeneration …
- **Spielautomat mit Synergien** – Symbol-Paare und Misch-Kombos geben Extra-Boni
- **Tages-Challenge** mit festem Seed, Modifikator & Streak
- **16 Erfolge** (dauerhaft über Runs) + Meta-Unlocks
- **Situationsabhängige Musik** (Menü / Karte / Kampf / Boss) – komplett
  synthetisiert, plus Drop-in für eigene Tracks
- **Pixel-Art-Grafik**, Screen-Shake, Partikel, „Juice"
- **In-Game-Auto-Update** über GitHub Releases (siehe unten)
- Spielstände bleiben **immer** gültig – ein Update wirft nie einen Save weg

## ⌨️ Steuerung

- **Maus**: alles anklickbar
- **1–7**: Handkarte spielen
- **Leertaste**: Slot drehen / Zug beenden / weiter
- **Esc**: Pause / zurück
- **M**: Ton an/aus

## ▶️ Spielen

**Einfachste Variante:** die fertige `SlotsAndSwords.exe` aus den
[Releases](https://github.com/bennetinname/slotsandswords/releases) laden und starten.
*(Windows zeigt bei der unsignierten EXE evtl. „Unbekannter Herausgeber" –
einmalig „Weitere Infos → Trotzdem ausführen".)*

**Aus dem Quellcode:**
```bash
pip install pygame
python main.py
```

## 🔄 Auto-Update

Beim Start prüft das Spiel im Hintergrund die GitHub-Releases. Gibt es eine neuere
Version, erscheint im Hauptmenü oben rechts ein **„🆕 Update laden"**-Button – ein
Klick lädt die neue EXE, tauscht sich selbst aus und startet neu. Kein erneutes
Verschicken der Datei nötig.

## 🛠️ Selbst bauen (Windows, One-File-EXE)

```bat
build_exe.bat
```
Erzeugt `dist\SlotsAndSwords.exe` (PyInstaller, `--onefile --windowed`, Assets
eingebündelt).

## 🧱 Tech / Aufbau

- `main.py` – Einstieg (pygame/Audio/Fenster)
- `game.py` – State-Machine & Spiellogik
- `ui.py` – komplettes Rendering
- `entities.py` – Spieler, Gegner, Karten
- `slots.py` – Spielautomat & Symbol-Effekte
- `card_effects.py` – Karteneffekte
- `constants.py` – Karten, Relikte, Gegner, Symbole, Version
- `mapgen.py` – Pfad-/Akt-Karten
- `audio.py` – prozeduraler Sound & Musik
- `updater.py` – In-Game-Auto-Update
- `savegame.py` / `options.py` / `highscores.py` / `daily.py` / `stats.py` /
  `achievements.py` – Persistenz
- `assets/` – Pixel-Art, Musik, Icons

Kein numpy/PIL zur Laufzeit nötig.

---

*Slots & Swords – ein Vibe-Coding-Experiment. Viel Spaß beim Zocken!* 🍀
