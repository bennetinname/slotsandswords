"""
Prozeduraler Sound & Musik – komplett synthetisiert, keine Asset-Dateien.
Robuster Fallback: läuft auch ohne funktionierende Audioausgabe (still).
"""

import io
import math
import wave
import struct
import random as _random

import pygame

SAMPLE_RATE = 44100

_enabled = False          # Mixer verfügbar?
_muted = False            # vom Spieler stummgeschaltet?
_sounds = {}              # name -> pygame.Sound
_music_sound = None
_music_channel = None
_spin_channel = None

# Lautstärken (0..1) – per Optionsmenü einstellbar
_master_vol = 0.8
_music_vol = 0.5
_sfx_vol = 0.6

# Manche Effekte sind von Natur aus laut -> Dämpfung pro Effekt
_PER_SOUND = {"click": 0.3, "reel": 0.7, "error": 0.7, "card": 0.85}


# ─────────────────────────────────────────────
# Synth-Bausteine (liefern Float-Listen in [-1, 1])
# ─────────────────────────────────────────────

def _osc(freq, dur, kind="sine", duty=0.5):
    n = int(SAMPLE_RATE * dur)
    out = [0.0] * n
    for i in range(n):
        ph = (freq * i / SAMPLE_RATE) % 1.0
        if kind == "sine":
            out[i] = math.sin(2 * math.pi * ph)
        elif kind == "square":
            out[i] = 1.0 if ph < duty else -1.0
        elif kind == "saw":
            out[i] = 2.0 * ph - 1.0
        elif kind == "triangle":
            out[i] = 4.0 * abs(ph - 0.5) - 1.0
        elif kind == "noise":
            out[i] = _random.uniform(-1.0, 1.0)
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


def _build_music():
    """Sanfter, schleifbarer Ambient-Loop (Moll-Arpeggio + Bass)"""
    # A-Moll-Pentatonik-Arpeggio
    notes = [220.0, 261.63, 329.63, 392.0, 329.63, 261.63]
    bass = [110.0, 110.0, 98.0, 98.0, 87.31, 87.31]
    note_dur = 0.42
    arp = []
    for i, fr in enumerate(notes * 2):
        arp = _cat(arp, _env(_osc(fr, note_dur, "triangle"), 0.02, note_dur * 0.5, 0.22))
    bs = []
    for fr in (bass * 2):
        seg = _env(_osc(fr, note_dur * 1.0, "sine"), 0.03, note_dur * 0.4, 0.18)
        bs = _cat(bs, seg)
    n = min(len(arp), len(bs))
    track = _mix(arp[:n], bs[:n])
    # leichtes Gesamt-Tremolo für Atmosphäre
    for i in range(len(track)):
        track[i] *= 0.85 + 0.15 * math.sin(2 * math.pi * 0.1 * i / SAMPLE_RATE)
    return _to_sound(track, gain=0.9)


# ─────────────────────────────────────────────
# Öffentliche API
# ─────────────────────────────────────────────

def init():
    """Initialisiert den Mixer und baut alle Sounds. Still bei Fehler."""
    global _enabled, _sounds, _music_sound, _music_channel, _spin_channel, _combo_sounds
    try:
        pygame.mixer.quit()
        pygame.mixer.init(SAMPLE_RATE, -16, 1, 512)
        pygame.mixer.set_num_channels(16)
        _sounds = _build_sounds()
        _combo_sounds = _build_combo_sounds()
        _music_sound = _build_music()
        _music_channel = pygame.mixer.Channel(0)
        _spin_channel = pygame.mixer.Channel(1)
        _enabled = True
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


def start_music():
    if not _enabled or _muted or not _music_channel or not _music_sound:
        return
    _music_channel.play(_music_sound, loops=-1)
    _music_channel.set_volume(_music_vol * _master_vol)


def stop_music():
    if _music_channel:
        _music_channel.stop()


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
