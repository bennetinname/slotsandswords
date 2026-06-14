"""
Prozeduraler Sound & Musik – komplett synthetisiert, keine Asset-Dateien.
Robuster Fallback: läuft auch ohne funktionierende Audioausgabe (still).
"""

import io
import os
import math
import wave
import struct
import threading
import random as _random

import pygame

try:
    import assets as _assets          # nur für den Asset-Basis-Pfad (Drop-in-Musik)
    _ASSET_BASE = _assets.BASE
except Exception:
    _ASSET_BASE = None

SAMPLE_RATE = 44100

_enabled = False          # Mixer verfügbar?
_muted = False            # vom Spieler stummgeschaltet?
_sounds = {}              # name -> pygame.Sound
_music_channel = None
_spin_channel = None

_music_cache = {}         # name -> pygame.Sound (im Hintergrund-Thread gebaut)
_music_lock = threading.Lock()
_current_music = None     # gewünschter Track-Name
_playing_track = None     # tatsächlich gerade laufender Track

# Lautstärken (0..1) – per Optionsmenü einstellbar
_master_vol = 0.8
_music_vol = 0.5
_sfx_vol = 0.6

# Manche Effekte sind von Natur aus laut -> Dämpfung pro Effekt
_PER_SOUND = {"click": 0.3, "reel": 0.7, "error": 0.7, "card": 0.85}


# ─────────────────────────────────────────────
# Synth-Bausteine (liefern Float-Listen in [-1, 1])
# ─────────────────────────────────────────────

_SINE_TABLE = [math.sin(2 * math.pi * i / 4096) for i in range(4096)]


def _osc(freq, dur, kind="sine", duty=0.5):
    n = int(SAMPLE_RATE * dur)
    out = [0.0] * n
    if kind == "noise":
        uni = _random.uniform
        for i in range(n):
            out[i] = uni(-1.0, 1.0)
        return out
    # Inkrementelle Phase (kein Multiplizieren/Modulo pro Sample)
    inc = freq / SAMPLE_RATE
    ph = 0.0
    if kind == "sine":
        tbl = _SINE_TABLE
        step = freq * 4096.0 / SAMPLE_RATE
        idx = 0.0
        for i in range(n):
            out[i] = tbl[int(idx) & 4095]
            idx += step
        return out
    for i in range(n):
        if kind == "square":
            out[i] = 1.0 if ph < duty else -1.0
        elif kind == "saw":
            out[i] = 2.0 * ph - 1.0
        else:  # triangle
            out[i] = 4.0 * abs(ph - 0.5) - 1.0
        ph += inc
        if ph >= 1.0:
            ph -= 1.0
    return out


def _sweep(f0, f1, dur, kind="sine"):
    """Frequenz-Sweep von f0 nach f1"""
    n = int(SAMPLE_RATE * dur)
    out = [0.0] * n
    phase = 0.0
    for i in range(n):
        t = i / max(1, n - 1)
        f = f0 + (f1 - f0) * t
        phase += f / SAMPLE_RATE
        ph = phase % 1.0
        if kind == "sine":
            out[i] = math.sin(2 * math.pi * ph)
        elif kind == "square":
            out[i] = 1.0 if ph < 0.5 else -1.0
        else:
            out[i] = 2.0 * ph - 1.0
    return out


def _env(samples, attack=0.01, release=0.08, hold=1.0):
    """Lineare Attack/Release-Hüllkurve (hold = Lautstärkefaktor)"""
    n = len(samples)
    a = int(SAMPLE_RATE * attack)
    r = int(SAMPLE_RATE * release)
    for i in range(n):
        if i < a:
            g = i / max(1, a)
        elif i > n - r:
            g = max(0.0, (n - i) / max(1, r))
        else:
            g = 1.0
        samples[i] *= g * hold
    return samples


def _mix(*tracks):
    """Mischt mehrere gleich/unterschiedlich lange Tracks additiv"""
    n = max(len(t) for t in tracks)
    out = [0.0] * n
    for t in tracks:
        for i, v in enumerate(t):
            out[i] += v
    return out


def _cat(*tracks):
    out = []
    for t in tracks:
        out.extend(t)
    return out


def _to_sound(samples, gain=1.0):
    """Float-Liste -> pygame.Sound (16-bit mono WAV im Speicher)"""
    buf = io.BytesIO()
    w = wave.open(buf, "wb")
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(SAMPLE_RATE)
    frames = bytearray()
    for v in samples:
        s = max(-1.0, min(1.0, v * gain))
        frames += struct.pack("<h", int(s * 32767))
    w.writeframes(bytes(frames))
    w.close()
    buf.seek(0)
    return pygame.mixer.Sound(file=buf)


# ─────────────────────────────────────────────
# Konkrete Effekte
# ─────────────────────────────────────────────

def _build_sounds():
    s = {}
    # Klick (kurzer Blip)
    s["click"] = _to_sound(_env(_osc(660, 0.05, "square"), 0.002, 0.04, 0.35))
    # Karte spielen (Wisch: Noise + Abwärts-Sweep)
    s["card"] = _to_sound(_env(_mix(_env(_osc(0, 0.12, "noise"), 0.005, 0.1, 0.2),
                                    _sweep(900, 400, 0.12)), 0.005, 0.09, 0.4))
    # Treffer (Noise-Burst + tiefer Thud)
    s["hit"] = _to_sound(_env(_mix(_env(_osc(0, 0.14, "noise"), 0.001, 0.12, 0.5),
                                   _sweep(220, 70, 0.14)), 0.001, 0.12, 0.55))
    # Block (zwei metallische Töne)
    s["block"] = _to_sound(_cat(_env(_osc(520, 0.05, "square"), 0.002, 0.04, 0.3),
                                _env(_osc(780, 0.06, "square"), 0.002, 0.05, 0.3)))
    # Heilung (aufsteigendes Arpeggio)
    s["heal"] = _to_sound(_cat(_env(_osc(523, 0.07, "sine"), 0.005, 0.05, 0.4),
                               _env(_osc(659, 0.07, "sine"), 0.005, 0.05, 0.4),
                               _env(_osc(784, 0.09, "sine"), 0.005, 0.07, 0.4)))
    # Gold (zwei helle Münz-Blips)
    s["gold"] = _to_sound(_cat(_env(_osc(1320, 0.05, "square"), 0.002, 0.04, 0.25),
                               _env(_osc(1760, 0.06, "square"), 0.002, 0.05, 0.25)))
    # Reel-Stop (Klick-Thunk)
    s["reel"] = _to_sound(_env(_mix(_env(_osc(0, 0.05, "noise"), 0.001, 0.04, 0.3),
                                    _sweep(300, 120, 0.05)), 0.001, 0.04, 0.5))
    # Spin-Loop (ratterndes Geräusch)
    rattle = []
    for _ in range(14):
        rattle = _cat(rattle, _env(_osc(0, 0.04, "noise"), 0.002, 0.02, 0.18),
                      [0.0] * int(SAMPLE_RATE * 0.02))
    s["spin"] = _to_sound(rattle)
    # Jackpot / Triple (Fanfare aufsteigend)
    jp = _cat(
        _env(_osc(523, 0.08, "square"), 0.003, 0.05, 0.3),
        _env(_osc(659, 0.08, "square"), 0.003, 0.05, 0.3),
        _env(_osc(784, 0.08, "square"), 0.003, 0.05, 0.3),
        _env(_osc(1047, 0.16, "square"), 0.003, 0.12, 0.35),
    )
    s["jackpot"] = _to_sound(jp)
    # Sieg (Major-Akkord-Arpeggio)
    s["win"] = _to_sound(_cat(
        _env(_osc(523, 0.1, "triangle"), 0.005, 0.06, 0.4),
        _env(_osc(659, 0.1, "triangle"), 0.005, 0.06, 0.4),
        _env(_osc(784, 0.1, "triangle"), 0.005, 0.06, 0.4),
        _env(_osc(1047, 0.25, "triangle"), 0.005, 0.2, 0.45),
    ))
    # Niederlage (absteigend, traurig)
    s["lose"] = _to_sound(_cat(
        _env(_osc(440, 0.16, "triangle"), 0.005, 0.1, 0.4),
        _env(_osc(349, 0.16, "triangle"), 0.005, 0.1, 0.4),
        _env(_osc(262, 0.35, "triangle"), 0.005, 0.28, 0.4),
    ))
    # Fehler (tiefer Buzz)
    s["error"] = _to_sound(_env(_osc(120, 0.16, "square"), 0.005, 0.1, 0.3))
    # Relikt (heller Glöckchen-Shimmer)
    s["relic"] = _to_sound(_cat(
        _env(_osc(1047, 0.09, "sine"), 0.003, 0.07, 0.35),
        _env(_osc(1568, 0.14, "sine"), 0.003, 0.12, 0.3),
    ))
    return s


def _build_combo_sounds():
    """Combo-Sounds mit steigender Tonhöhe je Stufe"""
    out = {}
    base = 600
    for lvl in range(2, 9):
        f = base * (1.0 + (lvl - 2) * 0.12)
        out[lvl] = _to_sound(_env(_osc(f, 0.07, "square"), 0.002, 0.05, 0.3))
    return out


_combo_sounds = {}


# ─────────────────────────────────────────────
# Musik-Engine: mehrere situationsabhängige Tracks
# ─────────────────────────────────────────────

# Gleichstufige Stimmung: Halbton-Offset (von A=220) -> Frequenz
def _hz(semis, base=220.0):
    return base * (2.0 ** (semis / 12.0))

# Akkord als Halbton-Offsets relativ zum Grundton
_MINOR = [0, 3, 7]
_MAJOR = [0, 4, 7]


def _compose(progression, minor=True, note_dur=0.34, octave=0, lead=True,
             hat=False, gain=0.9, bass_oct=-12, drive=False, _samples_only=False):
    """Baut einen schleifbaren Track aus einer Akkordfolge (Halbton-Grundtöne).
    Layer: Arpeggio + Bass + Pad (+ optional Lead-Melodie + Hi-Hat)."""
    chord_iv = _MINOR if minor else _MAJOR
    beats_per_chord = 4
    arp = []; bs = []; pad = []; lead_l = []; hatt = []
    rng = _random.Random(hash(tuple(progression)) & 0xffffffff)
    for root in progression:
        froot = _hz(root + octave)
        tones = [_hz(root + octave + iv) for iv in chord_iv]
        # Arpeggio (auf/ab durch die Akkordtöne)
        seq = tones + [tones[1]]
        for b in range(beats_per_chord):
            fr = seq[b % len(seq)]
            kind = "saw" if drive else "triangle"
            arp = _cat(arp, _env(_osc(fr, note_dur, kind), 0.012, note_dur * 0.45, 0.16))
        # Bass: Grundton, pro Akkord gehalten + Oktav-Puls
        bfr = _hz(root + bass_oct)
        bseg = _env(_osc(bfr, note_dur * beats_per_chord, "sine"), 0.02,
                    note_dur * beats_per_chord * 0.3, 0.30)
        bs = _cat(bs, bseg)
        # Pad: gehaltener Akkord, sehr leise (Fülle)
        pseg = _mix(*[_env(_osc(t, note_dur * beats_per_chord, "sine"),
                            note_dur, note_dur * beats_per_chord * 0.4, 0.05) for t in tones])
        pad = _cat(pad, pseg)
        # Lead: einzelne Akkordtöne mit Pausen (Melodie-Andeutung)
        if lead:
            for b in range(beats_per_chord):
                if rng.random() < 0.55:
                    fr = tones[rng.randint(0, len(tones) - 1)] * 2
                    lead_l = _cat(lead_l, _env(_osc(fr, note_dur, "square"),
                                               0.008, note_dur * 0.5, 0.07))
                else:
                    lead_l = _cat(lead_l, [0.0] * int(SAMPLE_RATE * note_dur))
        # Hi-Hat: kurzer Noise-Tick auf jedem Beat
        if hat:
            for b in range(beats_per_chord):
                tick = _env(_osc(0, 0.03, "noise"), 0.001, 0.025, 0.06 if b % 2 else 0.1)
                hatt = _cat(hatt, tick, [0.0] * int(SAMPLE_RATE * (note_dur - 0.03)))

    layers = [arp, bs, pad]
    if lead and lead_l:
        layers.append(lead_l)
    if hat and hatt:
        layers.append(hatt)
    n = min(len(l) for l in layers if l)
    track = _mix(*[l[:n] for l in layers])
    # sanftes Gesamt-Tremolo
    for i in range(len(track)):
        track[i] *= 0.9 + 0.1 * math.sin(2 * math.pi * 0.07 * i / SAMPLE_RATE)
    if _samples_only:
        return track, gain
    return _to_sound(track, gain=gain)


def _write_wav(samples, gain, path):
    """Schreibt Float-Samples als 16-bit Mono-WAV (für vorgerenderte Musik)."""
    w = wave.open(path, "wb")
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SAMPLE_RATE)
    frames = bytearray()
    for v in samples:
        s = max(-1.0, min(1.0, v * gain))
        frames += struct.pack("<h", int(s * 32767))
    w.writeframes(bytes(frames)); w.close()


def export_tracks(out_dir):
    """Rendert alle Tracks als WAV-Dateien (Build-Zeit-Tool, nicht zur Laufzeit)."""
    os.makedirs(out_dir, exist_ok=True)
    for name, recipe in _TRACK_RECIPES.items():
        samples, gain = _compose(_samples_only=True, **recipe)
        _write_wav(samples, gain, os.path.join(out_dir, name + ".wav"))


# Track-Rezepte (Akkordfolgen in Halbtönen relativ zu A).
# Längere, sich entwickelnde Folgen -> weniger eintönig.
_TRACK_RECIPES = {
    # Menü/Übersicht: warm, ruhig, leicht melancholisch
    "menu":    dict(progression=[0, -2, 5, 3, 0, -2, -4, -5], minor=True,
                    note_dur=0.42, lead=True, hat=False, gain=0.85),
    # Karte/Erkundung: neugierig, mittleres Tempo
    "explore": dict(progression=[0, 5, 3, 7, 0, 5, 8, 7], minor=True,
                    note_dur=0.34, lead=True, hat=True, gain=0.85),
    # Kampf: treibend, mehr Biss (Saw-Arp + Hi-Hat)
    "combat":  dict(progression=[0, 0, 5, 5, 3, 3, -2, 2], minor=True,
                    note_dur=0.24, lead=True, hat=True, gain=0.9, drive=True),
    # Boss: schnell, düster, gespannt
    "boss":    dict(progression=[0, -1, 0, -1, 5, 4, 7, 6], minor=True,
                    note_dur=0.20, lead=True, hat=True, gain=0.95, drive=True,
                    bass_oct=-24),
}


def _music_file(name):
    """Pfad zu einer echten Musikdatei (Drop-in), falls vorhanden, sonst None."""
    if not _ASSET_BASE:
        return None
    for ext in (".ogg", ".wav", ".mp3"):
        p = os.path.join(_ASSET_BASE, "music", name + ext)
        if os.path.exists(p):
            return p
    return None


def _build_track(name):
    """Synthese ODER echte Datei -> Sound. Langsam -> läuft im Hintergrund-Thread."""
    path = _music_file(name)
    if path:
        try:
            return pygame.mixer.Sound(path)
        except Exception:
            pass
    recipe = _TRACK_RECIPES.get(name) or _TRACK_RECIPES["menu"]
    try:
        return _compose(**recipe)
    except Exception:
        return None


def _get_track(name):
    """Gibt den fertigen Track zurück (oder None, solange noch nicht gebaut)."""
    return _music_cache.get(name)


def _prebuild_music():
    """Baut alle Tracks im Hintergrund (kein Freeze). Priorität: zuerst Menü/Kampf."""
    for name in ("menu", "combat", "explore", "boss"):
        if name in _music_cache:
            continue
        snd = _build_track(name)
        with _music_lock:
            _music_cache[name] = snd


# ─────────────────────────────────────────────
# Öffentliche API
# ─────────────────────────────────────────────

def init():
    """Initialisiert den Mixer und baut alle Sounds. Still bei Fehler."""
    global _enabled, _sounds, _music_channel, _spin_channel, _combo_sounds
    try:
        pygame.mixer.quit()
        pygame.mixer.init(SAMPLE_RATE, -16, 1, 512)
        pygame.mixer.set_num_channels(16)
        _sounds = _build_sounds()
        _combo_sounds = _build_combo_sounds()
        _music_channel = pygame.mixer.Channel(0)
        _spin_channel = pygame.mixer.Channel(1)
        _enabled = True
        # Musik-Tracks im Hintergrund vorbauen (kein Start-Freeze)
        threading.Thread(target=_prebuild_music, daemon=True).start()
    except Exception:
        _enabled = False


def _sfx_gain(vol=1.0):
    return vol * _sfx_vol * _master_vol


def play(name, vol=1.0):
    if not _enabled or _muted:
        return
    snd = _sounds.get(name)
    if snd:
        snd.set_volume(_sfx_gain(vol) * _PER_SOUND.get(name, 1.0))
        snd.play()


def click():
    """Dezenter UI-Klick (bewusst leise)."""
    play("click")


def play_combo(level):
    if not _enabled or _muted:
        return
    snd = _combo_sounds.get(min(8, max(2, level)))
    if snd:
        snd.set_volume(_sfx_gain(0.5))
        snd.play()


def start_spin():
    if not _enabled or _muted or not _spin_channel:
        return
    snd = _sounds.get("spin")
    if snd:
        snd.set_volume(_sfx_gain(0.45))
        _spin_channel.play(snd, loops=-1)


def stop_spin():
    if _spin_channel:
        _spin_channel.stop()


def play_music(name):
    """Wechselt zum Track <name> (menu/explore/combat/boss). Schon laufend -> nichts."""
    global _current_music, _playing_track
    _current_music = name
    if not _enabled or _muted or not _music_channel:
        return
    # läuft dieser Track schon? dann nicht neu starten (kein Stottern)
    if _playing_track == name and _music_channel.get_busy():
        return
    snd = _get_track(name)
    if not snd:
        return
    _music_channel.play(snd, loops=-1)
    _music_channel.set_volume(_music_vol * _master_vol)
    _playing_track = name


def start_music():
    """Startet/setzt Musik fort (Default: Menü-Track)."""
    play_music(_current_music or "menu")


def stop_music():
    global _playing_track
    if _music_channel:
        _music_channel.stop()
    _playing_track = None


def _refresh_music_volume():
    if _music_channel and _music_channel.get_busy():
        _music_channel.set_volume(_music_vol * _master_vol)


def set_master(v):
    global _master_vol
    _master_vol = min(1.0, max(0.0, float(v)))
    _refresh_music_volume()


def set_music(v):
    global _music_vol
    _music_vol = min(1.0, max(0.0, float(v)))
    _refresh_music_volume()


def set_sfx(v):
    global _sfx_vol
    _sfx_vol = min(1.0, max(0.0, float(v)))


def get_volumes():
    return _master_vol, _music_vol, _sfx_vol


def is_muted():
    return _muted


def toggle_mute():
    """Schaltet Ton an/aus. Gibt neuen Zustand zurück (True = stumm)."""
    global _muted
    _muted = not _muted
    if _muted:
        if _music_channel:
            _music_channel.stop()
        if _spin_channel:
            _spin_channel.stop()
    else:
        start_music()
    return _muted
