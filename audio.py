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
    # Akt-Abschluss-Jingle (kurze Triumph-Fanfare, heller als 'win')
    s["fanfare"] = _to_sound(_cat(
        _env(_osc(523, 0.09, "square"), 0.004, 0.05, 0.32),
        _env(_osc(659, 0.09, "square"), 0.004, 0.05, 0.32),
        _env(_osc(784, 0.09, "square"), 0.004, 0.05, 0.32),
        _env(_mix(_osc(1047, 0.30, "triangle"), _osc(1568, 0.30, "triangle")),
             0.004, 0.24, 0.30),
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

# Akkord als Halbton-Offsets relativ zum Grundton
_MINOR = [0, 3, 7]
_MAJOR = [0, 4, 7]


_MINOR_SCALE = [0, 2, 3, 5, 7, 8, 10]   # natürliches Moll


def _triad(root, qual):
    return [root, root + (4 if qual == "maj" else 3), root + 7]


def _osc2(freq, dur, kind, cents):
    """Zwei leicht verstimmte Oszillatoren -> wärmer, weniger steril."""
    a = _osc(freq, dur, kind)
    b = _osc(freq * (2.0 ** (cents / 1200.0)), dur, kind)
    return [(a[i] + b[i]) * 0.5 for i in range(len(a))]


def _seg(freq, dur, kind, vol, atk=0.012, rel=None, cents=0.0):
    if freq <= 0:
        return [0.0] * int(SAMPLE_RATE * dur)
    s = _osc2(freq, dur, kind, cents) if cents else _osc(freq, dur, kind)
    return _env(s, atk, dur * 0.5 if rel is None else rel, vol)


def _pad_to(seg, length):
    if len(seg) < length:
        seg = seg + [0.0] * (length - len(seg))
    return seg[:length]


def _lowpass(buf, a):
    """Einpoliger Tiefpass: nimmt Schärfe raus, klingt wärmer."""
    y = 0.0
    for i in range(len(buf)):
        y += a * (buf[i] - y)
        buf[i] = y
    return buf


def _softclip(buf):
    for i in range(len(buf)):
        x = buf[i]
        x = 1.0 if x > 1 else (-1.0 if x < -1 else x)
        buf[i] = x - (x * x * x) / 3.0
    return buf


def _compose(prog, key=220.0, note_dur=0.36, repeats=2, drums=0, lp=0.22,
             gain=0.8, lead_density=0.6, _samples_only=False):
    """Schleifbarer Track aus einer diatonischen Moll-Akkordfolge.
    prog = Liste von (grundton_halbton, 'min'/'maj'). Layer: Pad, Bass,
    Arpeggio, sparsame Melodie (stufenweise), optional sanfte Drums."""
    BS = int(SAMPLE_RATE * note_dur)
    mel, arp, bass, pad, dr = [], [], [], [], []
    rng = _random.Random((hash(tuple(prog)) ^ int(key)) & 0xffffffff)
    deg = 4  # Start-Skalengrad der Melodie
    for _rep in range(repeats):
        for (root, qual) in prog:
            tones = _triad(root, qual)
            chordset = set(t % 12 for t in tones)
            # Bass: Grundton (2 Beats) + Quinte (2 Beats), tiefe Oktave
            bass = _cat(bass, _pad_to(_seg(key * 0.5 * 2 ** (root / 12.0),
                                           note_dur * 2, "sine", 0.24, rel=note_dur, cents=4), 2 * BS))
            bass = _cat(bass, _pad_to(_seg(key * 0.5 * 2 ** ((root + 7) / 12.0),
                                           note_dur * 2, "sine", 0.19, rel=note_dur, cents=4), 2 * BS))
            # Pad: gehaltener Akkord, weich, leise
            pseg = _mix(*[_seg(key * 2 ** (t / 12.0), note_dur * 4, "triangle",
                               0.085, atk=note_dur * 0.6, rel=note_dur * 1.6, cents=7) for t in tones])
            pad = _cat(pad, _pad_to(pseg, 4 * BS))
            # Arpeggio: Akkordtöne im Muster Grund-Terz-Quinte-Terz
            pat = [0, 1, 2, 1]
            for b in range(4):
                fr = key * 2 ** (tones[pat[b]] / 12.0)
                arp = _cat(arp, _pad_to(_seg(fr, note_dur, "triangle", 0.11,
                                             atk=0.01, rel=note_dur * 0.55, cents=5), BS))
            # Melodie: stufenweise, Akkordton auf Schlag 1/3, viele Pausen
            for b in range(4):
                strong = b in (0, 2)
                rest_p = 0.12 if strong else (1.0 - lead_density) * 0.8
                if rng.random() < rest_p:
                    mel = _cat(mel, [0.0] * BS)
                    continue
                deg = max(0, min(13, deg + rng.choice([-2, -1, -1, 0, 1, 1, 2])))
                semi = _MINOR_SCALE[deg % 7] + 12 * (deg // 7)
                if strong and (semi % 12) not in chordset:
                    nearest = min(chordset, key=lambda c: abs(c - semi % 12))
                    semi = semi - semi % 12 + nearest
                fr = key * 2 ** ((semi + 12) / 12.0)   # eine Oktave über Basis
                mel = _cat(mel, _pad_to(_seg(fr, note_dur, "triangle", 0.16,
                                             atk=0.01, rel=note_dur * 0.6, cents=6), BS))
            # Drums: weicher Kick auf 1&3, dezente Snare auf 2&4
            if drums:
                for b in range(4):
                    if b in (0, 2):
                        k = _env(_sweep(120, 45, min(0.16, note_dur), "sine"), 0.001, 0.12, 0.55)
                        dr = _cat(dr, _pad_to(k, BS))
                    elif drums >= 2 and b in (1, 3):
                        s = _lowpass(_env(_osc(0, min(0.11, note_dur), "noise"), 0.001, 0.09, 0.16), 0.5)
                        dr = _cat(dr, _pad_to(s, BS))
                    else:
                        dr = _cat(dr, [0.0] * BS)

    layers = [pad, bass, arp, mel] + ([dr] if drums else [])
    n = min(len(l) for l in layers)
    track = _mix(*[l[:n] for l in layers])
    track = _lowpass(track, lp)              # Wärme
    # sehr sanftes Tremolo für „Atmen"
    for i in range(len(track)):
        track[i] *= 0.94 + 0.06 * math.sin(2 * math.pi * 0.08 * i / SAMPLE_RATE)
    track = _softclip(track)
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


# Track-Rezepte: diatonische Moll-Akkordfolgen (root-Halbton, Qualität).
_TRACK_RECIPES = {
    # Menü: i–VI–III–VII (klassisch, warm-melancholisch), ruhig
    "menu":    dict(prog=[(0, "min"), (8, "maj"), (3, "maj"), (10, "maj")],
                    key=220.0, note_dur=0.40, repeats=2, drums=0, lp=0.16,
                    gain=0.80, lead_density=0.5),
    # Karte/Erkundung: i–III–VII–VI, etwas Bewegung, leichter Kick
    "explore": dict(prog=[(0, "min"), (3, "maj"), (10, "maj"), (8, "maj")],
                    key=220.0, note_dur=0.34, repeats=2, drums=1, lp=0.24,
                    gain=0.80, lead_density=0.6),
    # Kampf: i–VI–VII–V(dur), treibend mit Kick+Snare
    "combat":  dict(prog=[(0, "min"), (8, "maj"), (10, "maj"), (7, "maj")],
                    key=196.0, note_dur=0.27, repeats=2, drums=2, lp=0.34,
                    gain=0.85, lead_density=0.7),
    # Boss: i–VI–iv–V(dur), düster, schnell, tiefere Tonart
    "boss":    dict(prog=[(0, "min"), (8, "maj"), (5, "min"), (7, "maj")],
                    key=165.0, note_dur=0.23, repeats=2, drums=2, lp=0.40,
                    gain=0.90, lead_density=0.7),
}

# ── Musik PRO AKT ───────────────────────────────────────────────────
# Je Akt-Thema ein eigener Charakter (Tonart/Tempo/Akkordfolge/Wärme).
# Für jede Rolle (explore/combat/boss) wird daraus ein Rezept gebaut.
# Track-Namen: f"{rolle}_a{index}" (index 0..5). Fällt auf das Basis-
# Rezept zurück, falls ein Akt-Track (noch) fehlt.
_ACT_FLAVORS = [
    # 0 Die Kneipe – warm, gemütlich, leicht schwingend
    dict(key=220.0, dur=0.34, lp=0.20,
         prog=[(0, "min"), (8, "maj"), (3, "maj"), (10, "maj")]),
    # 1 Untergrund-Casino – heller, jazzig-frech, treibend
    dict(key=247.0, dur=0.30, lp=0.30,
         prog=[(0, "min"), (5, "min"), (10, "maj"), (7, "maj")]),
    # 2 Verfluchtes Reich – unheimlich, schwebend, dunkel
    dict(key=185.0, dur=0.36, lp=0.16,
         prog=[(0, "min"), (1, "maj"), (8, "maj"), (7, "maj")]),
    # 3 Kanalisation – grimmig, tief, stampfend
    dict(key=174.0, dur=0.30, lp=0.34,
         prog=[(0, "min"), (3, "maj"), (5, "min"), (10, "maj")]),
    # 4 Frostpalast – kalt, klar, hoch & sparsam
    dict(key=262.0, dur=0.38, lp=0.12,
         prog=[(0, "min"), (10, "maj"), (8, "maj"), (3, "maj")]),
    # 5 Unterwelt – infernalisch, schnell, ganz tief
    dict(key=147.0, dur=0.24, lp=0.42,
         prog=[(0, "min"), (8, "maj"), (5, "min"), (6, "maj")]),
]

_ROLE_PARAMS = {
    "explore": dict(repeats=2, drums=1, gain=0.80, lead_density=0.55, dur_mul=1.0),
    "combat":  dict(repeats=2, drums=2, gain=0.85, lead_density=0.7, dur_mul=0.82),
    "boss":    dict(repeats=2, drums=2, gain=0.90, lead_density=0.75, dur_mul=0.68),
}


def _act_recipe(role, idx):
    fl = _ACT_FLAVORS[idx % len(_ACT_FLAVORS)]
    rp = _ROLE_PARAMS[role]
    key = fl["key"]
    if role == "boss":
        key *= 0.75          # Boss tiefer/bedrohlicher
    return dict(prog=fl["prog"], key=key, note_dur=fl["dur"] * rp["dur_mul"],
                repeats=rp["repeats"], drums=rp["drums"], lp=fl["lp"],
                gain=rp["gain"], lead_density=rp["lead_density"])


# Akt-Rezepte vorab registrieren (werden nur bei Bedarf synthetisiert).
for _i in range(len(_ACT_FLAVORS)):
    for _role in ("explore", "combat", "boss"):
        _TRACK_RECIPES[f"{_role}_a{_i}"] = _act_recipe(_role, _i)


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


_building = set()   # Tracks, die gerade im Hintergrund gebaut werden


def _get_track(name):
    """Gibt den fertigen Track zurück. Fehlt er, wird er im Hintergrund
    gebaut (kein Freeze); bis dahin Fallback auf die Basis-Rolle, sonst None."""
    snd = _music_cache.get(name)
    if snd is not None:
        return snd
    if name in _music_cache:
        return None                      # bewusst None gecacht (Build fehlgeschlagen)
    # Build anstoßen (einmalig)
    if name not in _building and name in _TRACK_RECIPES:
        _building.add(name)
        threading.Thread(target=_bg_build, args=(name,), daemon=True).start()
    # Solange noch nichts da ist: auf Basis-Rolle ausweichen (z.B. 'combat')
    base = name.split("_a")[0]
    if base != name:
        return _music_cache.get(base)
    return None


MUSIC_CACHE_MAX = 6          # max. gleichzeitig gehaltene Tracks (RAM-Cap)
_lru = []                    # Track-Namen, zuletzt benutzt zuletzt


def _touch(name):
    """Markiert einen Track als zuletzt benutzt (für LRU-Eviction)."""
    if name in _lru:
        _lru.remove(name)
    _lru.append(name)


def _evict_music():
    """Verwirft die ältesten Tracks über dem Cap (nie den laufenden)."""
    while len(_music_cache) > MUSIC_CACHE_MAX:
        victim = next((n for n in _lru if n != _playing_track), None)
        if victim is None:
            break
        _lru.remove(victim)
        _music_cache.pop(victim, None)


def _bg_build(name):
    snd = _build_track(name)
    with _music_lock:
        _music_cache[name] = snd
        _touch(name)
        _evict_music()
    _building.discard(name)


def _prebuild_music():
    """Baut die zuerst benötigten Tracks im Hintergrund vor (kein Start-Freeze).
    Akt-Tracks werden erst bei Bedarf gebaut (spart RAM)."""
    for name in ("menu", "combat", "explore"):
        if name in _music_cache:
            continue
        snd = _build_track(name)
        with _music_lock:
            _music_cache[name] = snd
            _touch(name)


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
    with _music_lock:
        _touch(name)


def start_music():
    """Startet/setzt Musik fort (Default: Menü-Track)."""
    play_music(_current_music or "menu")


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
