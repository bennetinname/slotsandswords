# Slots & Swords — Projektleitfaden für Claude

Roguelike-Kartenspiel-Spielautomat in **Python + pygame** (kein numpy/PIL zur
Laufzeit nötig; PIL nur fürs App-Icon). Endlos: Pfad-Karte mit Akten, nach
jedem Boss ein „Akt geschafft"-Screen, dann weiter.

## Starten & Bauen
- Spiel starten: `python main.py`
- EXE bauen (One-File, Windows): `build_exe.bat`
  (PyInstaller `--onefile --windowed --icon icon.ico --add-data "assets;assets"`)
- Ergebnis: `dist\SlotsAndSwords.exe` — eine Datei, Assets sind eingebündelt.

## Architektur (Module)
- `main.py` — Einstieg: pygame init, Audio, Fenster, startet `Game`.
- `game.py` — zentrale State-Machine (Menü, Map, Kampf, Slot, Shop, Event,
  Rest, Pause, Options, Changelog, ActClear, GameOver). Spiel-Logik & Flow.
- `ui.py` — `UIRenderer`: ALLES Zeichnen (Panels, Karten, Status, Map,
  Tooltips ...). Zeichnet auf eine Canvas; `game.run()` blittet sie mit
  Screen-Shake-Versatz aufs Fenster.
- `entities.py` — `Player`, `Enemy`, `Card`.
- `slots.py` — Slot-Maschine + Symbol-Effekte.
- `card_effects.py` — Karteneffekt-Auflösung.
- `constants.py` — Farben, Werte, `GAME_VERSION`, `CHANGELOG`, `ENEMY_TYPES`,
  `CARD_DEFINITIONS`, `RELIC_DEFINITIONS`, `EVENT_DEFINITIONS`, `SLOT_SYMBOLS`.
- `mapgen.py` — Pfad-/Akt-Karte (reine Daten, serialisierbar).
- `audio.py` — prozeduraler Sound + Musik (synthetisiert), Lautstärken.
- `savegame.py` / `options.py` / `highscores.py` — Persistenz (JSON).
- `paths.py` — STABILER Datenpfad (siehe unten). 
- `assets.py` — Sprite-Lader mit Cache + Procedural-Fallback.

## Wichtige Konventionen
- **Versionierung:** Bei jedem Release `GAME_VERSION` in `constants.py` erhöhen,
  oben in `CHANGELOG` EINE kurze Zeile ergänzen (wird in-game unter „Was ist
  neu" gezeigt), und einen Abschnitt in `CHANGELIST.txt` (ausführlich).
  Danach EXE neu bauen.
- **Save-Kompatibilität (HARTE REGEL):** Spielstände müssen IMMER gültig
  bleiben — ein Update darf NIEMALS einen Save verwerfen. `savegame.load_save`
  hat KEINEN Versions-Check mehr (lädt versionsunabhängig). Deshalb: neue
  Save-Felder NUR additiv mit Default, und in `_deserialize_*` (game.py) jedes
  Feld defensiv per `.get(...)` lesen. Versionsnummer (Minor/Patch) ist fürs
  Speichern egal. NIE den Versions-Gate wieder einbauen.
- **Laufzeitdaten** (`highscores.json`, `savegame.json`, `options.json`) IMMER
  über `paths.data_path(...)` schreiben — nicht relativ/`__file__`! In der
  One-File-EXE zeigt `__file__` in den temporären `_MEI`-Ordner, der beim
  Beenden gelöscht wird (das war der Highscore-„verschwindet"-Bug).
- **Assets:** liegen in `assets/<kategorie>/<name>.png`. Laden über
  `assets.load/scaled/fit/by_height`. Fehlt eine Datei -> Procedural-Fallback,
  nichts bricht. Neue Assets müssen über `--add-data` mit in die EXE.
- **Gegner/Events** referenzieren ihr Sprite per `"asset"`-Key in den Defs.

## Assets schneiden (neue Sheets)
- Sheets kommen mit **Magenta-Hintergrund** (#FF00FF), Sprites klar abgegrenzt.
- Vorgehen: Magenta als Hintergrund erkennen, **Connected-Components** (Inseln)
  finden, Text-Labels per Größe rausfiltern, pro Sprite zuschneiden, Magenta
  transparent keyen (global, damit hohle Rahmen transparente Mitte bekommen),
  eng trimmen, nach `assets/<kat>/` speichern. (Temp-Tool danach löschen.)

## Testen (headless)
- `SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy` setzen, `pygame.display.set_mode`,
  dann `Game` durch States treiben und Frames rendern.
- Screenshots mit `pygame.image.save(...)` schreiben und per Bild-Anzeige
  prüfen (Crops vergrößern für Detailcheck). Maus-Hover lässt sich im Dummy-
  Treiber NICHT simulieren (Pos klebt bei 0,0) — Hover-Logik per Rect testen.
- Vor dem Bauen alte `SlotsAndSwords`-Prozesse beenden (sonst Lock auf die EXE).

## Kampf-Layout (Kurzreferenz)
- Spieler-Avatar links (unter Spieler-HP), Gegner rechts (unter Gegner-HP),
  „Slot drehen" mittig über dem Kampflog. FX-Anker: `ENEMY_FX`/`PLAYER_FX`.

## Wo nachschauen
- `CHANGELIST.txt` — vollständige Versionshistorie/Begründungen.
- `TODO/TODO.txt` — Ideen/offene Punkte (inkl. Schwierigkeits-Ideen).
- `git log --oneline` — Commit-Verlauf (jede Version = 1 Commit).
- `TODO/assets_prompt.txt` — Stil-Prompts + noch benötigte Assets
  (Akt-Hintergründe, neue Relikt-Icons, Klassen-Portraits …).

Aktueller Stand: siehe `GAME_VERSION` in `constants.py`.
