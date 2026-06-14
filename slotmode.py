"""
Reiner Slot-Modus (Balatro-artig) – ein komplett eigenes Spiel ohne
Kartenkampf. Du baust einen Automaten auf (Symbol-Beutel + Joker) und musst
pro Runde eine wachsende Zielpunktzahl knacken. Score = Chips x Multiplikator.

Reine Daten/Logik (kein pygame) -> headless testbar. UI liegt in ui.py,
die Steuerung in game.py.
"""

import json
import random

import paths
from constants import SLOT_SYMBOLS

BEST_FILE = "slotmode.json"

# Emoji je Symbol (für die UI), aus den globalen Slot-Symbolen.
EMOJI = {s["name"]: s.get("emoji", "?") for s in SLOT_SYMBOLS}

# Chip-Grundwert je Symbol. Höher = seltener/wertvoller.
SYM_VALUE = {
    "CHERRY": 4, "CLOVER": 5, "BEER": 5, "DICE": 6, "HEART": 6, "SKULL": 7,
    "CHICKEN": 7, "SHIELD": 7, "MONEY": 8, "SNAKE": 8, "CLOWN": 8,
    "FIRE": 9, "LIGHTNING": 9, "STAR": 10, "VORTEX": 10, "TARGET": 11,
    "BOMB": 12, "MOON": 12, "CROWN": 15, "DIAMOND": 20,
}

# Start-Beutel: solide Mischung günstiger Symbole (Name -> Anzahl).
START_BAG = {"CHERRY": 4, "CLOVER": 3, "BEER": 3, "HEART": 3, "DICE": 3,
             "MONEY": 2, "SKULL": 2, "STAR": 1, "FIRE": 1}

SPINS_PER_ROUND = 5

# ─── Joker ────────────────────────────────────────────────────────────
# Jeder Joker verändert die Wertung (chips/mult) abhängig von den 3 Symbolen.
# fn(names, chips, mult) -> (chips, mult, beschreibung|None)
JOKERS = [
    {"id": "clover_luck", "emoji": "🍀", "name": "Glückskleeblatt", "cost": 22,
     "desc": "+3 Mult, wenn ein 🍀 erscheint."},
    {"id": "gold_vein",   "emoji": "💰", "name": "Goldader", "cost": 20,
     "desc": "+6 Chips pro 💰."},
    {"id": "twins",       "emoji": "👯", "name": "Zwillinge", "cost": 24,
     "desc": "Ein Paar gibt +3 extra Mult."},
    {"id": "variety",     "emoji": "🌈", "name": "Vielfalt", "cost": 26,
     "desc": "Alle 3 verschieden: Mult x2."},
    {"id": "reaper",      "emoji": "💀", "name": "Totenkopf-Sammler", "cost": 18,
     "desc": "+4 Chips pro 💀."},
    {"id": "fireworks",   "emoji": "🔥", "name": "Feuerwerk", "cost": 20,
     "desc": "+5 Chips pro 🔥."},
    {"id": "diamond_hand", "emoji": "💎", "name": "Diamanthand", "cost": 30,
     "desc": "💎 zählt doppelt (Chips)."},
    {"id": "chicken_farm", "emoji": "🐔", "name": "Hühnerfarm", "cost": 22,
     "desc": "+1 Mult pro 🐔."},
    {"id": "high_roller",  "emoji": "🎲", "name": "Hochroller", "cost": 25,
     "desc": "+2 Mult, aber nur bei mind. 25 Chips."},
    {"id": "crown_jewel",  "emoji": "👑", "name": "Kronjuwel", "cost": 28,
     "desc": "👑 gibt zusätzlich +4 Mult."},
]
JOKER_BY_ID = {j["id"]: j for j in JOKERS}


def _count(names, sym):
    return sum(1 for n in names if n == sym)


def _apply_joker(jid, names, chips, mult):
    """Wendet einen Joker auf die laufende Wertung an. Gibt (chips, mult, note)."""
    c, m, note = chips, mult, None
    if jid == "clover_luck" and "CLOVER" in names:
        m += 3; note = "🍀 +3 Mult"
    elif jid == "gold_vein":
        n = _count(names, "MONEY")
        if n: c += 6 * n; note = f"💰 +{6*n} Chips"
    elif jid == "twins":
        # Paar (genau zwei gleiche)
        if any(_count(names, s) == 2 for s in set(names)):
            m += 3; note = "👯 +3 Mult"
    elif jid == "variety":
        if len(set(names)) == 3:
            m *= 2; note = "🌈 Mult x2"
    elif jid == "reaper":
        n = _count(names, "SKULL")
        if n: c += 4 * n; note = f"💀 +{4*n} Chips"
    elif jid == "fireworks":
        n = _count(names, "FIRE")
        if n: c += 5 * n; note = f"🔥 +{5*n} Chips"
    elif jid == "diamond_hand":
        n = _count(names, "DIAMOND")
        if n: c += SYM_VALUE["DIAMOND"] * n; note = "💎 doppelt"
    elif jid == "chicken_farm":
        n = _count(names, "CHICKEN")
        if n: m += n; note = f"🐔 +{n} Mult"
    elif jid == "high_roller":
        if chips >= 25: m += 2; note = "🎲 +2 Mult"
    elif jid == "crown_jewel":
        n = _count(names, "CROWN")
        if n: m += 4 * n; note = f"👑 +{4*n} Mult"
    return c, m, note


def load_best():
    try:
        with open(paths.data_path(BEST_FILE), "r", encoding="utf-8") as f:
            return int(json.load(f).get("best_round", 0))
    except Exception:
        return 0


def save_best(round_reached):
    try:
        if round_reached <= load_best():
            return
        with open(paths.data_path(BEST_FILE), "w", encoding="utf-8") as f:
            json.dump({"best_round": int(round_reached)}, f)
    except Exception:
        pass


class SlotRun:
    """Ein Slot-Modus-Lauf: Beutel aufbauen, Zielpunktzahlen knacken."""

    def __init__(self):
        self.bag = dict(START_BAG)
        self.values = dict(SYM_VALUE)          # erlaubt dauerhafte Upgrades
        self.jokers = []                       # Liste von Joker-IDs
        self.round = 1
        self.gold = 8
        self.best_round = load_best()
        self.game_over = False
        self.in_shop = False
        self.shop = []                         # aktuelle Shop-Angebote
        self.reroll_cost = 5
        self.last_lines = []                   # Wertungs-Zeilen des letzten Spins
        self.last_total = 0
        self.log = []                          # kurze Verlaufstexte
        self._begin_round()

    # ── Runden-Setup ────────────────────────────────────────────
    def target_for(self, r):
        # Sanft wachsend, aber endlos fordernd: ~30, 70, 122, 190, 277, ...
        return int(30 * r * (1.18 ** (r - 1)))

    def _begin_round(self):
        self.target = self.target_for(self.round)
        self.spins_left = SPINS_PER_ROUND
        self.round_score = 0
        self.last_lines = []
        self.last_total = 0
        self.in_shop = False
        self.log = [f"Runde {self.round}: erreiche {self.target} Punkte in "
                    f"{SPINS_PER_ROUND} Drehs!"]

    # ── Spin & Wertung ──────────────────────────────────────────
    def draw_symbols(self):
        names = list(self.bag)
        weights = [self.bag[n] for n in names]
        return [random.choices(names, weights)[0] for _ in range(3)]

    def score(self, names):
        """Reine Wertung (testbar): gibt (total, lines)."""
        lines = []
        chips = sum(self.values.get(n, 5) for n in names)
        mult = 1
        lines.append((f"Symbole: {' '.join(EMOJI.get(n,'?') for n in names)}",
                      f"{chips} Chips"))
        uniq = set(names)
        # Paare / Drillinge
        if len(uniq) == 1:
            v = self.values.get(names[0], 5)
            chips += 2 * v; mult += 4
            lines.append(("DRILLING!", f"+{2*v} Chips, +4 Mult"))
        else:
            for s in uniq:
                if _count(names, s) == 2:
                    v = self.values.get(s, 5)
                    chips += v; mult += 2
                    lines.append((f"Paar {EMOJI.get(s,'?')}", f"+{v} Chips, +2 Mult"))
            if len(uniq) == 3:
                chips += 5
                lines.append(("Alle verschieden", "+5 Chips"))
        # Joker
        for jid in self.jokers:
            chips, mult, note = _apply_joker(jid, names, chips, mult)
            if note:
                j = JOKER_BY_ID.get(jid, {})
                lines.append((f"{j.get('emoji','?')} {j.get('name','Joker')}", note))
        total = chips * mult
        lines.append(("ERGEBNIS", f"{chips} x {mult} = {total}"))
        return total, lines

    def resolve_spin(self, names):
        """Wertet einen (bereits gedrehten) Spin und schreibt Zustand fort."""
        total, lines = self.score(names)
        self.last_lines = lines
        self.last_total = total
        self.round_score += total
        self.spins_left -= 1
        if self.round_score >= self.target:
            self._round_clear()
        elif self.spins_left <= 0:
            self.game_over = True
            self.best_round = max(self.best_round, self.round)
            save_best(self.round)
            self.log = [f"Geschafft bis Runde {self.round}. "
                        f"{self.round_score}/{self.target} – knapp daneben!"]
        return total, lines

    def _round_clear(self):
        # Belohnung: Basis + Bonus für übrige Drehs + Zins auf Gold
        reward = 6 + max(0, self.spins_left) * 3 + min(6, self.gold // 4)
        self.gold += reward
        self.best_round = max(self.best_round, self.round)
        save_best(self.round)
        self.in_shop = True
        self.reroll_cost = 5
        self.shop = self._roll_shop()
        self.log = [f"Runde {self.round} geknackt! +{reward} Chips "
                    f"(übrige Drehs: {self.spins_left})."]

    # ── Shop ────────────────────────────────────────────────────
    def _roll_shop(self):
        offers = []
        # 1 Symbol-Angebot (fügt ein Symbol dem Beutel hinzu -> bessere Chancen)
        sym = random.choice(list(self.values))
        offers.append({"kind": "symbol", "sym": sym,
                       "cost": 5 + self.values[sym] // 3,
                       "label": f"+1 {EMOJI.get(sym,'?')} in den Beutel"})
        # 1 Upgrade-Angebot (erhöht den Chip-Wert eines Beutel-Symbols dauerhaft)
        up = random.choice(list(self.bag))
        offers.append({"kind": "upgrade", "sym": up, "cost": 8,
                       "label": f"{EMOJI.get(up,'?')} {up}: +3 Chip-Wert"})
        # 1 Joker-Angebot (falls noch welche frei)
        free = [j for j in JOKERS if j["id"] not in self.jokers]
        if free and len(self.jokers) < 5:
            j = random.choice(free)
            offers.append({"kind": "joker", "joker": j["id"], "cost": j["cost"],
                           "label": f"{j['emoji']} {j['name']}"})
        return offers

    def can_afford(self, offer):
        return self.gold >= offer["cost"]

    def buy(self, offer):
        if offer.get("bought") or not self.can_afford(offer):
            return False
        self.gold -= offer["cost"]
        if offer["kind"] == "symbol":
            self.bag[offer["sym"]] = self.bag.get(offer["sym"], 0) + 1
        elif offer["kind"] == "upgrade":
            self.values[offer["sym"]] = self.values.get(offer["sym"], 5) + 3
        elif offer["kind"] == "joker":
            if offer["joker"] not in self.jokers:
                self.jokers.append(offer["joker"])
        offer["bought"] = True
        return True

    def reroll(self):
        if self.gold < self.reroll_cost:
            return False
        self.gold -= self.reroll_cost
        self.reroll_cost += 3
        self.shop = self._roll_shop()
        return True

    def next_round(self):
        self.round += 1
        self._begin_round()
