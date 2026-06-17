"""
SLOT-MODUS 2.0 – "DAS LOCH"

Ein eigenständiges Slot-Roguelike mit dem KLASSISCHEN 3-Walzen-Automaten
(dieselben Symbol-Sprites wie im Kampf). Jede Runde musst du die QUOTE
("Miete") aus deinem Münztopf zusammendrehen, sonst kommt die Hand durch den
Schlitz (Game Over). Schaffst du sie, wird die Miete abgezogen – der Rest
bleibt zum Einkaufen. Negative Symbole bestrafen dich, Glück (🍀) hält sie in
Schach, Charms bauen deinen Build. Es wird endlos härter.

Reine Daten/Logik (kein pygame) -> headless testbar. Anzeige übernimmt die
echte SlotMachine (slots.py); UI-Rahmen in ui.py, Steuerung in game.py.
"""

import json
import random

import paths
from constants import SLOT_SYMBOLS

BEST_FILE = "slotmode.json"

EMOJI = {s["name"]: s.get("emoji", "?") for s in SLOT_SYMBOLS}

# ── Symbol-Münzwerte ──────────────────────────────────────────────────
SYM_VALUE = {
    "CHERRY": 2, "BEER": 2, "DICE": 2, "BELL": 3, "HEART": 3, "CLOVER": 3,
    "CHICKEN": 3, "SKULL": 3, "SHIELD": 3, "SNAKE": 3,
    "MONEY": 4, "FIRE": 4, "LIGHTNING": 4, "CLOWN": 4,
    "STAR": 5, "VORTEX": 5, "TARGET": 6, "MOON": 6, "BOMB": 7,
    "CROWN": 8, "GEM": 9, "DIAMOND": 12,
    "WILD": 0,            # Joker: ersetzt jedes Symbol
    "TRAP": 0, "PIT": 0, "CURSE": 0,   # NEGATIV
}

NEGATIVE = {"TRAP", "PIT", "CURSE"}
WILD = "WILD"

# Start-Beutel: konzentriert auf wenige günstige Symbole (höhere Paar-Chance!)
START_BAG = {
    "CHERRY": 6, "BEER": 5, "DICE": 5, "HEART": 4, "CLOVER": 4,
    "MONEY": 3, "BELL": 3,
    "WILD": 1, "TRAP": 2, "PIT": 1, "CURSE": 1,
}

SPINS_PER_ROUND = 6

# ── Charms (Build-Anker, reichhaltig) ─────────────────────────────────
CHARMS = [
    {"id": "clover_luck",  "emoji": "🍀", "name": "Vierblättriges Glück", "cost": 6,
     "desc": "+2 Glück pro 🍀 (statt +1). Glück hält Pech-Symbole fern."},
    {"id": "gold_vein",    "emoji": "💰", "name": "Goldader", "cost": 6,
     "desc": "+4 Münzen pro 💰 im Dreh."},
    {"id": "wild_magnet",  "emoji": "🎰", "name": "Joker-Magnet", "cost": 9,
     "desc": "Jeder 🎰 gibt zusätzlich +6 Münzen."},
    {"id": "twins",        "emoji": "👯", "name": "Zwillinge", "cost": 5,
     "desc": "Ein Paar gibt +3 Mult (statt +1)."},
    {"id": "triple_crown", "emoji": "👑", "name": "Dreikrone", "cost": 8,
     "desc": "Ein Drilling gibt +5 Mult extra."},
    {"id": "variety",      "emoji": "🌈", "name": "Vielfalt", "cost": 7,
     "desc": "Alle 3 Symbole verschieden? Mult ×2."},
    {"id": "reaper",       "emoji": "💀", "name": "Sensenmann", "cost": 5,
     "desc": "+4 Münzen pro 💀 im Dreh."},
    {"id": "arsonist",     "emoji": "🔥", "name": "Brandstifter", "cost": 5,
     "desc": "+4 Münzen pro 🔥 im Dreh."},
    {"id": "diamond_hand", "emoji": "💎", "name": "Diamanthand", "cost": 10,
     "desc": "💎 zählen doppelt (Münzwert)."},
    {"id": "chicken_farm", "emoji": "🐔", "name": "Hühnerfarm", "cost": 5,
     "desc": "+2 Mult pro 🐔 im Dreh."},
    {"id": "high_roller",  "emoji": "🎲", "name": "Hochroller", "cost": 7,
     "desc": "Gewinnst du ≥30 Münzen in einem Dreh: nochmal +50%."},
    {"id": "lucky_seven",  "emoji": "🍀", "name": "Glücksbringer", "cost": 8,
     "desc": "Bei ≥5 Glück: +2 Mult. Bei ≥10 Glück: +4 Mult."},
    {"id": "exorcist",     "emoji": "🧿", "name": "Exorzist", "cost": 7,
     "desc": "🧿-Flüche wirken nicht mehr gegen dich."},
    {"id": "trap_smith",   "emoji": "🪤", "name": "Fallensteller", "cost": 7,
     "desc": "🪤 schaden nicht mehr – sie geben sogar +3 Münzen."},
    {"id": "bridge",       "emoji": "🕳️", "name": "Brücke", "cost": 7,
     "desc": "🕳️ Gruben ziehen keine Münzen mehr ab."},
    {"id": "interest",     "emoji": "🏦", "name": "Zinskonto", "cost": 9,
     "desc": "Nach jedem Dreh: +1 Münze pro 8 im Topf (max +8)."},
    {"id": "moonlight",    "emoji": "🌙", "name": "Mondlicht", "cost": 6,
     "desc": "🌙 gibt +3 Mult, wenn es dein letzter Dreh ist."},
    {"id": "bomber",       "emoji": "💣", "name": "Bomber", "cost": 8,
     "desc": "+6 Münzen pro 💣 im Dreh."},
    {"id": "gem_cutter",   "emoji": "💍", "name": "Edelsteinschleifer", "cost": 8,
     "desc": "+6 Münzen pro 💍 im Dreh."},
    {"id": "star_caller",  "emoji": "⭐", "name": "Sternenrufer", "cost": 7,
     "desc": "Jeder ⭐ gibt +2 Mult."},
    {"id": "scavenger",    "emoji": "🦴", "name": "Aasgeier", "cost": 6,
     "desc": "Pro übrigem Dreh am Rundenende: +6 Münzen Bonus."},
    {"id": "overclock",    "emoji": "⚡", "name": "Übertakter", "cost": 9,
     "desc": "Grund-Mult startet bei 2 statt 1."},
]
CHARM_BY_ID = {c["id"]: c for c in CHARMS}

# ── Telefon-Deals (Risiko/Belohnung) ──────────────────────────────────
PHONE_DEALS = [
    {"id": "free_charm", "label": "„Geschenk“: Gratis-Charm, aber +2 🧿 in den Beutel.",
     "good": "charm", "bad": ("bag", "CURSE", 2)},
    {"id": "loan", "label": "„Kredit“: +20 Münzen sofort – nächste Quote +40%.",
     "good": ("coins", 20), "bad": ("quota_mult", 1.4)},
    {"id": "cleanse", "label": "„Reinigung“: Entferne 3 Pech-Symbole – kostet 10 Münzen.",
     "good": ("cleanse", 3), "bad": ("coins", -10)},
    {"id": "double", "label": "„Alles oder nichts“: Münzen ×2 – aber +3 🪤 in den Beutel.",
     "good": ("coins_mult", 2.0), "bad": ("bag", "TRAP", 3)},
    {"id": "extra_spin", "label": "„Verlängerung“: +1 Dreh DAUERHAFT – kostet 16 Münzen.",
     "good": ("extra_spin", 1), "bad": ("coins", -16)},
]


def _count(seq, sym):
    return sum(1 for n in seq if n == sym)


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
    """Ein Lauf im Slot-Modus 'Das Loch' (klassischer 3-Walzen-Automat)."""

    def __init__(self):
        self.bag = dict(START_BAG)
        self.values = dict(SYM_VALUE)
        self.charms = []                  # Liste von Charm-IDs (max 6)
        self.round = 1
        self.coins = 18
        self.lucky = 0
        self.spins_per_round = SPINS_PER_ROUND
        self.best_round = load_best()
        self.game_over = False
        self.in_shop = False
        self.shop = []
        self.phone = None
        self.reroll_cost = 4
        self.last_result = ["CHERRY", "CHERRY", "CHERRY"]  # die 3 Symbole
        self.last_lines = []
        self.last_total = 0
        self._quota_mult = 1.0
        self.log = []
        self._begin_round()

    # ── Runden-Setup ────────────────────────────────────────────
    def quota_for(self, r):
        """Sanft, dann fordernd wachsend."""
        base = int(27 * r * (1.12 ** (r - 1)))
        return int(base * self._quota_mult)

    def _begin_round(self):
        self.quota = self.quota_for(self.round)
        self._quota_mult = 1.0
        self.spins_left = self.spins_per_round
        self.in_shop = False
        self.phone = None
        self.last_lines = []
        self.log = [f"Runde {self.round}: Dreh dir {self.quota} Münzen für die Miete!"]

    # ── Ziehen (3 Symbole, mit Glücks-Filter gegen Pech) ────────
    def draw_symbols(self):
        names = list(self.bag)
        weights = [self.bag[n] for n in names]
        res = [random.choices(names, weights)[0] for _ in range(3)]
        if self.lucky > 0:
            p = min(0.7, 0.08 * self.lucky)
            good = [n for n in names if n not in NEGATIVE]
            gw = [self.bag[n] for n in good]
            if good:
                for i, n in enumerate(res):
                    if n in NEGATIVE and random.random() < p:
                        res[i] = random.choices(good, gw)[0]
        return res

    # ── Wertung (3 Symbole) ─────────────────────────────────────
    def _best_match(self, names):
        """Bestes Match: (sym, count) oder None. WILD ersetzt jedes Symbol."""
        w = names.count(WILD)
        reals = [s for s in names if s != WILD]
        if not reals:
            return (WILD, 3)              # alles Wild
        best = None
        for s in set(reals):
            if s in NEGATIVE:
                continue
            total = reals.count(s) + w
            if total >= 2:
                val = self.values.get(s, 1)
                if best is None or (total, val) > (best[1], self.values.get(best[0], 1)):
                    best = (s, min(3, total))
        return best

    def score(self, names):
        """Reine Wertung (testbar): (total, lines)."""
        lines = []
        emj = " ".join(EMOJI.get(n, "?") for n in names)
        lines.append((f"Walzen: {emj}", ""))

        chips = sum(self.values.get(n, 0) for n in names if n not in NEGATIVE)
        mult = 2 if "overclock" in self.charms else 1

        # Paar / Drilling
        m = self._best_match(names)
        if m:
            sym, count = m
            base = 8 if sym == WILD else self.values.get(sym, 1)
            if count == 3:
                add = base * 8
                chips += add
                lines.append((f"DRILLING {EMOJI.get(sym,'?')}", f"+{add} Chips"))
                if "triple_crown" in self.charms:
                    mult += 5; lines.append(("👑 Dreikrone", "+5 Mult"))
            else:
                add = base * 2
                chips += add
                lines.append((f"Paar {EMOJI.get(sym,'?')}", f"+{add} Chips"))
                if "twins" in self.charms:
                    mult += 3; lines.append(("👯 Zwillinge", "+3 Mult"))
        elif len(set(names)) == 3:
            lines.append(("Alle verschieden", ""))

        def cnt(s):
            return _count(names, s)

        # Münz-Boni-Charms
        for cid, sym, per, label in [
            ("gold_vein", "MONEY", 4, "💰 Goldader"),
            ("reaper", "SKULL", 4, "💀 Sensenmann"),
            ("arsonist", "FIRE", 4, "🔥 Brandstifter"),
            ("bomber", "BOMB", 6, "💣 Bomber"),
            ("gem_cutter", "GEM", 6, "💍 Schleifer"),
            ("wild_magnet", "WILD", 6, "🎰 Joker-Magnet"),
        ]:
            if cid in self.charms:
                n = cnt(sym)
                if n:
                    chips += per * n
                    lines.append((label, f"+{per*n} Chips"))
        if "diamond_hand" in self.charms and cnt("DIAMOND"):
            extra = self.values.get("DIAMOND", 12) * cnt("DIAMOND")
            chips += extra
            lines.append(("💎 Diamanthand", f"+{extra} Chips"))

        # Mult-Charms
        if "chicken_farm" in self.charms and cnt("CHICKEN"):
            mult += 2 * cnt("CHICKEN")
            lines.append(("🐔 Hühnerfarm", f"+{2*cnt('CHICKEN')} Mult"))
        if "star_caller" in self.charms and cnt("STAR"):
            mult += 2 * cnt("STAR")
            lines.append(("⭐ Sternenrufer", f"+{2*cnt('STAR')} Mult"))
        if "moonlight" in self.charms and cnt("MOON") and self.spins_left <= 1:
            mult += 3 * cnt("MOON")
            lines.append(("🌙 Mondlicht", f"+{3*cnt('MOON')} Mult"))
        if "variety" in self.charms and len(set(names)) == 3:
            mult *= 2
            lines.append(("🌈 Vielfalt", "Mult ×2"))
        if "lucky_seven" in self.charms:
            if self.lucky >= 10:
                mult += 4; lines.append(("🍀 Glücksbringer", "+4 Mult"))
            elif self.lucky >= 5:
                mult += 2; lines.append(("🍀 Glücksbringer", "+2 Mult"))

        gross = chips * mult

        # Negativ-Symbole
        penalty = 0
        if "CURSE" in names and "exorcist" not in self.charms:
            c = cnt("CURSE")
            cut = int(gross * min(0.75, 0.25 * c))
            if cut:
                penalty += cut
                lines.append((f"🧿 Fluch ×{c}", f"-{cut}"))
        if "PIT" in names and "bridge" not in self.charms:
            c = cnt("PIT")
            penalty += 4 * c
            lines.append((f"🕳️ Grube ×{c}", f"-{4*c}"))
        if "TRAP" in names:
            c = cnt("TRAP")
            if "trap_smith" in self.charms:
                gross += 3 * c
                lines.append((f"🪤 Fallensteller ×{c}", f"+{3*c}"))
            else:
                penalty += 3 * c
                lines.append((f"🪤 Falle ×{c}", f"-{3*c}"))

        total = max(0, gross - penalty)
        if "high_roller" in self.charms and total >= 30:
            boost = total // 2
            total += boost
            lines.append(("🎲 Hochroller", f"+{boost}"))

        lines.append(("ERGEBNIS", f"{chips} × {mult} = {total}"))
        return total, lines

    def resolve_spin(self, names):
        total, lines = self.score(names)
        clovers = _count(names, "CLOVER")
        if clovers:
            per = 2 if "clover_luck" in self.charms else 1
            self.lucky = min(20, self.lucky + per * clovers)
        self.last_result = list(names)
        self.last_lines = lines
        self.last_total = total
        self.coins += total
        if "interest" in self.charms and self.coins > 0:
            self.coins += min(8, self.coins // 8)
        self.spins_left -= 1
        if self.spins_left <= 0:
            self._settle()
        return total, lines

    def _settle(self):
        if self.coins >= self.quota:
            self.coins -= self.quota
            self.best_round = max(self.best_round, self.round)
            save_best(self.round)
            self.in_shop = True
            self.reroll_cost = 4
            self.shop = self._roll_shop()
            self.phone = self._maybe_phone()
            self.log = [f"Miete bezahlt! −{self.quota} Münzen. Rest: {self.coins}."]
        else:
            self.game_over = True
            self.best_round = max(self.best_round, self.round)
            save_best(self.round)
            self.log = [f"Die Hand kommt durch den Schlitz … "
                        f"{self.coins}/{self.quota} – Miete nicht geschafft."]

    def cash_out_early(self):
        if self.coins < self.quota or self.in_shop or self.game_over:
            return False
        if "scavenger" in self.charms and self.spins_left > 0:
            bonus = 6 * self.spins_left
            self.coins += bonus
            self.log = [f"🦴 Aasgeier: +{bonus} Münzen für {self.spins_left} übrige Drehs."]
        self.spins_left = 0
        self._settle()
        return True

    # ── Shop / Telefon ──────────────────────────────────────────
    def _roll_shop(self):
        offers = []
        free = [c for c in CHARMS if c["id"] not in self.charms]
        if free and len(self.charms) < 6:
            j = random.choice(free)
            offers.append({"kind": "charm", "charm": j["id"], "cost": j["cost"],
                           "label": f"{j['emoji']} {j['name']}"})
        good = [s for s in self.values if s not in NEGATIVE and s != WILD]
        sym = random.choice(good)
        offers.append({"kind": "symbol", "sym": sym,
                       "cost": 3 + self.values.get(sym, 3) // 2,
                       "label": f"+1 {EMOJI.get(sym,'?')} in den Beutel"})
        up = random.choice([s for s in self.bag if s not in NEGATIVE and s != WILD] or good)
        offers.append({"kind": "upgrade", "sym": up, "cost": 6,
                       "label": f"{EMOJI.get(up,'?')} {up}: +2 Münzwert"})
        bad_in_bag = [s for s in self.bag if s in NEGATIVE and self.bag[s] > 0]
        if bad_in_bag:
            rm = random.choice(bad_in_bag)
            offers.append({"kind": "remove", "sym": rm, "cost": 5,
                           "label": f"Entferne 1 {EMOJI.get(rm,'?')} aus dem Beutel"})
        else:
            offers.append({"kind": "spin", "cost": 14,
                           "label": "+1 Dreh pro Runde (dauerhaft)"})
        offers.append({"kind": "symbol", "sym": "WILD", "cost": 9,
                       "label": "+1 🎰 (Joker) in den Beutel"})
        random.shuffle(offers)
        return offers[:4]

    def _maybe_phone(self):
        if random.random() < 0.35:
            return dict(random.choice(PHONE_DEALS), taken=False)
        return None

    def can_afford(self, offer):
        cost = offer.get("cost", 0)
        return self.coins >= cost if cost >= 0 else True

    def buy(self, offer):
        if offer.get("bought") or not self.can_afford(offer):
            return False
        self.coins -= offer["cost"]
        k = offer["kind"]
        if k == "charm":
            if offer["charm"] not in self.charms:
                self.charms.append(offer["charm"])
        elif k == "symbol":
            self.bag[offer["sym"]] = self.bag.get(offer["sym"], 0) + 1
        elif k == "upgrade":
            self.values[offer["sym"]] = self.values.get(offer["sym"], 3) + 2
        elif k == "remove":
            s = offer["sym"]
            if self.bag.get(s, 0) > 0:
                self.bag[s] -= 1
                if self.bag[s] <= 0:
                    del self.bag[s]
        elif k == "spin":
            self.spins_per_round += 1
        offer["bought"] = True
        return True

    def reroll(self):
        if self.coins < self.reroll_cost:
            return False
        self.coins -= self.reroll_cost
        self.reroll_cost += 2
        self.shop = self._roll_shop()
        return True

    def take_phone(self):
        if not self.phone or self.phone.get("taken"):
            return False
        deal = self.phone
        self._apply_phone_part(deal["good"])
        self._apply_phone_part(deal["bad"])
        deal["taken"] = True
        return True

    def _apply_phone_part(self, part):
        if part == "charm":
            free = [c for c in CHARMS if c["id"] not in self.charms]
            if free and len(self.charms) < 6:
                self.charms.append(random.choice(free)["id"])
            return
        tag = part[0]
        if tag == "coins":
            self.coins = max(0, self.coins + part[1])
        elif tag == "coins_mult":
            self.coins = int(self.coins * part[1])
        elif tag == "quota_mult":
            self._quota_mult = part[1]
        elif tag == "bag":
            self.bag[part[1]] = self.bag.get(part[1], 0) + part[2]
        elif tag == "cleanse":
            removed = 0
            for s in list(NEGATIVE):
                while self.bag.get(s, 0) > 0 and removed < part[1]:
                    self.bag[s] -= 1
                    if self.bag[s] <= 0:
                        del self.bag[s]
                    removed += 1
        elif tag == "extra_spin":
            self.spins_per_round += part[1]

    def next_round(self):
        self.round += 1
        self._begin_round()
