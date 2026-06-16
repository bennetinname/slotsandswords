"""Kern-Spielklassen: Spieler, Gegner, Karten"""

import random
from constants import *

# Emojis für die Symbole des Slot-Bosses (Jackpot-Automat)
SLOT_BOSS_EMOJI = {"SKULL": "💀", "HEART": "❤️", "TRAP": "🪤", "SHIELD": "🛡️",
                   "MONEY": "💰", "FIRE": "🔥", "DICE": "🎲"}


class Card:
    """Eine Karte im Deck des Spielers"""
    
    def __init__(self, definition):
        self.name = definition["name"]
        self.type = definition["type"]
        self.cost = definition["cost"]
        self.damage = definition.get("damage", 0)
        self.block = definition.get("block", 0)
        self.heal = definition.get("heal", 0)
        self.color = definition["color"]
        self.tooltip = definition["tooltip"]
        self.rarity = definition.get("rarity", "common")
        self.effect = definition.get("effect", "damage")
        self.exhaust = definition.get("exhaust", False)
        self.upgraded = False
        self.selected = False
        self.hovered = False
        self.rect = None

    def can_upgrade(self):
        """Flüche und bereits verbesserte Karten können nicht aufgewertet werden"""
        return not self.upgraded and self.type != "curse"

    def upgrade(self):
        """Wertet die Karte dauerhaft auf (+50% Werte, Specials -1 Kosten)"""
        if not self.can_upgrade():
            return False
        import math
        if self.damage > 0:
            self.damage = int(math.ceil(self.damage * 1.5))
        if self.block > 0:
            self.block = int(math.ceil(self.block * 1.5))
        if self.heal > 0:
            self.heal = int(math.ceil(self.heal * 1.5))
        # Reine Effekt-Karten ohne Werte: Kosten senken
        if self.damage == 0 and self.block == 0 and self.heal == 0 and self.cost > 0:
            self.cost -= 1
        self.upgraded = True
        if not self.name.endswith("+"):
            self.name += "+"
        return True

    def get_rarity_color(self):
        return {
            "common":   GREY,
            "uncommon": BLUE,
            "rare":     GOLD,
            "curse":    CURSE_COL,
        }.get(self.rarity, GREY)

    def get_type_icon(self):
        return {
            "attack":  "⚔️",
            "defense": "🛡️",
            "special": "✨",
            "curse":   "💀",
        }.get(self.type, "?")

    # Karteneffekt -> Sprite in assets/cards/ (Effekt-Icon auf der Karte)
    EFFECT_ICONS = {
        "damage": "atk_slash", "double_strike": "atk_slash", "rage": "atk_slash",
        "iron_storm": "atk_slash", "retribution": "atk_slash", "expose": "atk_slash",
        "lifesteal": "atk_slash",
        "block": "defense_shield", "shield_wall": "defense_shield",
        "spike_skin": "defense_shield", "reflect": "defense_shield",
        "heal": "heal_herb", "second_wind": "heal_herb", "regen_potion": "heal_herb",
        "nuke": "death_skull", "execrate": "death_skull", "annihilate": "death_skull",
        "last_resort": "death_skull", "berserker": "death_skull", "executioner": "death_skull",
        "blood_pact": "death_skull",
        "curse_nausea": "death_skull", "curse_unluck": "death_skull", "curse_burden": "death_skull",
        # Gift-Karten -> eigenes Gift-Icon (v1.9.1)
        "poison_blade": "poison_vial", "toxic_cloud": "poison_vial", "acid_barrel": "poison_vial",
        "plague_breath": "poison_vial", "brew_poison": "poison_vial", "bloodletting": "poison_vial",
        "gambling": "dice_chaos", "coinflip": "dice_chaos", "all_in": "dice_chaos",
        "roulette": "dice_chaos", "chaos": "dice_chaos",
        "greed": "gold_coin", "bribe": "gold_coin", "pillage": "gold_coin",
        "gold_rush": "gold_coin", "coin_rain": "gold_coin", "tax_evasion": "gold_coin",
        "adrenaline": "energy_bolt", "redraw": "energy_bolt", "shadow_step": "energy_bolt",
        "card_trick": "energy_bolt",
        # Glücks-/Spin-Karten -> Klee-Icon (v1.9.1)
        "lucky_streak": "luck_clover", "double_spin": "luck_clover", "triple_spin": "luck_clover",
        "loaded_dice": "luck_clover", "lucky_hit": "luck_clover",
        # Stärke-Karten -> Faust-Icon (v1.9.1)
        "warcry": "strength_fist", "train": "strength_fist",
        "shield_bash": "shield_bash",
        "chicken": "chicken", "chicken_swarm": "chicken",
        # Karten v1.10.0
        "blade_flurry": "atk_slash", "execute_low": "death_skull", "backhand": "atk_slash",
        "sunder": "atk_slash", "midas": "gold_coin",
        "poison_dart": "poison_vial", "venom_burst": "poison_vial",
        "counter": "defense_shield", "evade": "defense_shield",
        "energize": "energy_bolt", "deep_draw": "energy_bolt",
        "berserk_rage": "strength_fist", "meditate": "strength_fist",
        # Karten v1.12.0
        "frost_strike": "atk_slash", "icestorm": "atk_slash", "stun_bash": "atk_slash",
        "mark_strike": "atk_slash", "flurry5": "atk_slash", "ambush": "atk_slash",
        "feast": "atk_slash", "bloodrage": "atk_slash",
        "doom_card": "death_skull", "soul_cut": "death_skull", "judgement": "death_skull",
        "entrench": "defense_shield", "frost_armor": "defense_shield",
        "endure": "defense_shield", "cleanse": "defense_shield",
        "rage_power": "strength_fist", "focus_power": "strength_fist",
        "sacrifice_card": "strength_fist",
        "rush": "energy_bolt", "mega_poison": "poison_vial", "wild_luck": "luck_clover",
    }

    def get_effect_icon(self):
        """Asset-Name des Effekt-Icons (in assets/cards/). Fallback nach Typ."""
        n = self.name.lower()
        if "fire" in n or "feuer" in n or "brand" in n or "flame" in n:
            return "fire"
        icon = Card.EFFECT_ICONS.get(self.effect)
        if icon:
            return icon
        return {"attack": "atk_slash", "defense": "defense_shield",
                "special": "energy_bolt", "curse": "death_skull"}.get(self.type, "atk_slash")


class Player:
    """Der Spieler mit HP, Deck, Hand, Gold und Status"""

    def __init__(self, class_def=None):
        self.class_def = class_def
        self.class_id = class_def["id"] if class_def else None
        self.max_hp = PLAYER_MAX_HP
        self.hp = PLAYER_MAX_HP
        self.gold = PLAYER_START_GOLD
        self.block = 0
        self.energy = PLAYER_ENERGY_PER_TURN
        self.max_energy = PLAYER_ENERGY_PER_TURN
        
        # Status-Effekte
        self.burn = 0          # Schaden pro Runde (sinkt um 1)
        self.poison = 0        # Gift: Schaden pro Runde, ignoriert Block (sinkt um 1)
        self.regen = 0         # Regeneration: heilt pro Runde (sinkt um 1)
        self.thorns = 0        # Dornen: reflektiert Schaden bei Gegnertreffer (ganzer Kampf)
        self.strength = 0      # Schadensbonus DIESEN Kampf (resettet je Kampf)
        self.perm_strength = 0 # dauerhafte Stärke-Basis (nur seltene Quellen)
        self.lucky = 0         # Slot-Bonus-Runden
        self.shield_up = False # Doppel-Block diese Runde
        self.reflect = False   # Reflektiert nächsten Schaden
        self.dodge = False     # Weicht dem nächsten Gegnerangriff aus
        # ─── Neue Statuseffekte (v1.12.0) ───
        self.vulnerable = 0    # Spieler nimmt +50% Schaden (Runden, sinkt um 1)
        self.rage = 0          # +X Stärke zu JEDEM Rundenstart (bleibt ganzen Kampf)
        self.focus = 0         # nächste Angriffskarte macht +X Schaden (einmalig)
        self.flat_reduction = 0     # Pauschale Schadensreduktion pro Treffer (Kettenhemd)
        self.has_phoenix = False    # Phönixfeder aktiv?
        self.phoenix_used = False   # einmal pro RUN
        self._phoenix_triggered = False  # für Log im Spiel
        self.coin_rain_active = False  # +Gold je gespielter Karte
        self.next_free_card = False    # Nächste Karte kostet 0 (Schattenschritt)
        self._total_damage_taken = 0   # Gesamtschaden über den Run (für Vergeltung)
        
        # Deck-System
        self.deck = []
        self.hand = []
        self.discard = []

        # Relikte (permanente passive Boni)
        self.relics = []   # Liste von Relikt-Dicts
        
        # Heilungs-Multiplikator (Tages-Challenge "Giftiger Boden")
        self.heal_mult = 1.0

        # Statistiken
        self.best_combo = 0
        self.damage_dealt = 0
        self.gold_earned = 0
        self.slots_spun = 0
        self.chickens_summoned = 0
        self.enemies_defeated = 0
        
        # Slot-Spins diese Runde (Double/Triple Spin)
        self.bonus_spins = 0
        
        self._build_starter_deck()
    
    def _build_starter_deck(self):
        """Startdeck mit 10 Karten – klassenspezifisch, sonst Standard."""
        if self.class_def and self.class_def.get("deck"):
            starter_cards = list(self.class_def["deck"])
        else:
            starter_cards = [
                "Schneller Stich", "Schneller Stich", "Schneller Stich",
                "Schwertstreich", "Schwertstreich",
                "Schild", "Schild",
                "Heilkraut",
                "Greed",
                "Coin Flip",
            ]
        for name in starter_cards:
            for defn in CARD_DEFINITIONS:
                if defn["name"] == name:
                    self.deck.append(Card(defn))
                    break
        random.shuffle(self.deck)
    
    def draw_hand(self, count=None):
        """
        Zieht Karten. Ohne 'count' wird bis PLAYER_DRAW_PER_TURN nachgezogen,
        aber maximal bis PLAYER_MAX_HAND. Ungespielte Karten bleiben so erhalten,
        weil die Hand nicht vorher geleert wird.
        """
        if count is None:
            # Ziehe so viele, dass die Hand um PLAYER_DRAW_PER_TURN wächst,
            # aber nie über das Maximum.
            target = min(PLAYER_MAX_HAND, len(self.hand) + PLAYER_DRAW_PER_TURN)
            to_draw = target - len(self.hand)
        else:
            to_draw = min(count, PLAYER_MAX_HAND - len(self.hand))
        
        drawn = 0
        while drawn < to_draw:
            if not self.deck:
                if not self.discard:
                    break  # Keine Karten mehr verfügbar
                # Abwurfstapel neu mischen
                self.deck = self.discard[:]
                self.discard = []
                random.shuffle(self.deck)
            if self.deck:
                self.hand.append(self.deck.pop())
                drawn += 1
        return drawn
    
    def draw_initial_hand(self):
        """Zieht die volle Starthand zu Kampfbeginn"""
        self.hand = []
        self.draw_hand(PLAYER_HAND_SIZE)
    
    def start_turn(self):
        """Rundenstart: Energie auffüllen, Karten nachziehen (Block bleibt erhalten!)"""
        self.energy = self.max_energy
        self.bonus_spins = 0
        self.reflect = False
        self.coin_rain_active = False
        self.next_free_card = False
        if self.shield_up:
            self.shield_up = False
        # Wut: +X Stärke zu jedem Rundenstart (Aufbau über den Kampf)
        if self.rage > 0:
            self.strength += self.rage
        # Verwundbar baut pro Runde ab
        if self.vulnerable > 0:
            self.vulnerable -= 1
        # Gegengift-Relikt: kein Gift auf dir
        if any(r.get("id") == "antidote" for r in self.relics):
            self.poison = 0
        # Regeneration zuerst (heilen vor dem DoT fühlt sich fairer an)
        if self.regen > 0:
            self.heal_hp(self.regen)
            self.regen -= 1
        # Burn-Schaden
        if self.burn > 0:
            self.take_damage(self.burn, ignore_block=True)
            self.burn = max(0, self.burn - 1)
        # Gift-Schaden (ignoriert Block, sinkt um 1)
        if self.poison > 0:
            self.take_damage(self.poison, ignore_block=True)
            self.poison -= 1
        # Nachziehen bis zu einer ZUFÄLLIGEN Ziel-Handgröße (Hand-RNG):
        # mal eine fette Hand, mal eine magere – ungespielte Karten bleiben.
        target = random.randint(HAND_RNG_MIN, HAND_RNG_MAX)
        need = target - len(self.hand)
        if need > 0:
            self.draw_hand(need)
    
    def take_damage(self, amount, ignore_block=False):
        """Nimmt Schaden, reduziert durch Block"""
        # Verwundbar: +50% erlittener Schaden (vor Block)
        if self.vulnerable > 0 and amount > 0:
            amount = int(amount * 1.5)
        if not ignore_block:
            absorbed = min(self.block, amount)
            self.block -= absorbed
            amount -= absorbed
            # Kettenhemd: pauschale Reduktion nur auf echte Treffer
            if amount > 0 and self.flat_reduction > 0:
                amount = max(0, amount - self.flat_reduction)
        self.hp = max(0, self.hp - amount)
        if amount > 0:
            self._total_damage_taken += amount
        # Phönixfeder: einmal pro Run den Tod überleben
        if self.hp <= 0 and self.has_phoenix and not self.phoenix_used:
            self.phoenix_used = True
            self.hp = 1
            self._phoenix_triggered = True
        return amount  # tatsächlicher Schaden
    
    def heal_hp(self, amount):
        """Heilt HP bis zum Maximum (heal_mult z.B. für Tages-Modifikatoren)"""
        old = self.hp
        amount = int(amount * self.heal_mult)
        self.hp = min(self.max_hp, self.hp + amount)
        return self.hp - old
    
    def add_gold(self, amount):
        self.gold += amount
        self.gold_earned += amount
    
    def spend_gold(self, amount):
        if self.gold >= amount:
            self.gold -= amount
            return True
        return False
    
    def add_card_to_deck(self, card_def):
        """Fügt neue Karte zum Abwurfstapel hinzu"""
        self.discard.append(Card(card_def))

    def has_relic(self, relic_id):
        """Prüft ob ein Relikt im Besitz ist"""
        return any(r["id"] == relic_id for r in self.relics)

    def add_relic(self, relic_def):
        """Fügt ein Relikt hinzu, wendet Sofort-Effekte an. Gibt False bei Duplikat."""
        if self.has_relic(relic_def["id"]):
            return False
        self.relics.append(relic_def)
        # Sofort wirkende Relikte
        if relic_def["id"] == "bonus_energy":
            self.max_energy += 1
        elif relic_def["id"] == "max_hp_relic":
            self.max_hp += 20
            self.hp += 20
        elif relic_def["id"] == "combat_strength":
            # NERF: einmaliger Bonus beim Aufheben statt +2 pro Kampf (kein Schneeball)
            self.strength += 3
        return True

    def is_alive(self):
        return self.hp > 0


class Enemy:
    """Ein Gegner mit HP, Schaden und KI"""
    
    def __init__(self, enemy_type: dict):
        self.name = enemy_type["name"]
        self.hp = enemy_type["hp"]
        self.max_hp = enemy_type["max_hp"]
        self.damage = enemy_type["damage"]
        self._base_damage = self.damage   # für Schaden-Eskalations-Deckel
        self.armor = enemy_type.get("armor", 0)
        self.block = 0
        self.gold_reward = enemy_type["gold_reward"]
        self.color = enemy_type["color"]
        self.tooltip = enemy_type["tooltip"]
        self.tier = enemy_type.get("tier", 1)
        self.is_boss = enemy_type.get("is_boss", False)
        self.is_elite = enemy_type.get("is_elite", False)

        # Sprite-Asset (None -> prozedurale Darstellung)
        self.asset = enemy_type.get("asset")

        # Einzigartige Mechanik
        self.mechanic = enemy_type.get("mechanic")
        self._undying_used = False
        self.jam_next = False        # manipuliert nächste Slot-Runde des Spielers
        self.turn_count = 0
        self.last_slot = None        # Slot-Boss: zuletzt gedrehte Symbole (für UI)
        self.last_slot_timer = 0.0

        # Status
        self.burn = 0
        self.poison = 0     # Gift: tickt jede Runde, sinkt NICHT (Build-up-Archetyp)
        self.vulnerable = 0 # Runden mit +50% Schadensaufnahme
        self.weakened = 0   # Runden mit halbiertem Schaden
        # ─── Neue Statuseffekte (v1.12.0) ───
        self.frost = 0      # Frost: Angriffsschaden -50% für N Runden
        self.stunned = 0    # Betäubt: überspringt N Züge komplett
        self.doom = 0       # Verhängnis: Countdown, dann massiver Schlag
        self.marked = 0     # Markiert: nimmt +X Bonus-Schaden pro Treffer
        
        # KI: Was plant der Gegner diese Runde?
        self.intent = "attack"
        self.intent_value = self.damage
        self._randomize_intent()
    
    def _block_value(self):
        """Block-Wert beim Verteidigen – skaliert mit dem (tiefenabhängigen)
        Schaden, damit später nicht mehr der Anfangs-Block kommt (TODO #3)."""
        return max(8, int(self.damage * 0.85))

    def _randomize_intent(self):
        """Bestimmt die nächste Aktion des Gegners"""
        roll = random.random()
        if self.mechanic == "slot_boss":
            self.intent = "spin"           # dreht seinen eigenen Automaten
            self.intent_value = 0
            return
        if self.is_boss:
            # Bosse: gefährlich, aber mit Verschnaufpausen (fairer)
            if roll < 0.45:
                self.intent = "attack"
                self.intent_value = self.damage
            elif roll < 0.58:
                self.intent = "heavy_attack"
                self.intent_value = int(self.damage * 1.5)
            elif roll < 0.74:
                self.intent = "defend"
                self.intent_value = self._block_value()
            else:
                self.intent = "taunt"
                self.intent_value = 0
        elif self.mechanic == "reckless":
            # Betrunkener Ritter: entweder wuchtig oder er stolpert
            if roll < 0.45:
                self.intent = "heavy_attack"
                self.intent_value = int(self.damage * 1.7)
            elif roll < 0.75:
                self.intent = "attack"
                self.intent_value = self.damage
            else:
                self.intent = "taunt"
                self.intent_value = 0
        elif self.mechanic == "roulette_foe":
            # Roulette-Geist: setzt alles auf eine Zahl – Doppelschlag oder Niete
            if roll < 0.5:
                self.intent = "heavy_attack"
                self.intent_value = self.damage * 2
            else:
                self.intent = "taunt"   # "Niete" – verfehlt komplett
                self.intent_value = 0
        elif self.mechanic == "gambler_foe":
            # Würfelgnom: völlig unberechenbar
            if roll < 0.4:
                self.intent = "attack"
                self.intent_value = random.randint(2, max(3, self.damage + 2))
            elif roll < 0.6:
                self.intent = "heavy_attack"
                self.intent_value = int(self.damage * 1.6)
            elif roll < 0.8:
                self.intent = "defend"
                self.intent_value = self._block_value()
            else:
                self.intent = "taunt"
                self.intent_value = 0
        else:
            if roll < 0.65:
                self.intent = "attack"
                self.intent_value = self.damage
            elif roll < 0.80:
                self.intent = "defend"
                self.intent_value = self._block_value()
            elif roll < 0.92:
                self.intent = "taunt"
                self.intent_value = 0
            else:
                self.intent = "heavy_attack"
                self.intent_value = int(self.damage * 1.5)

        # Kneipenschläger: unter halben HP schlägt er 50% härter zu
        if (self.mechanic == "enrage" and self.hp < self.max_hp // 2
                and self.intent in ("attack", "heavy_attack")):
            self.intent_value = int(self.intent_value * 1.5)

    def try_undying(self):
        """Lich/Sensenmann: einmal pro Kampf den Tod überleben. Gibt Log oder None."""
        if self.hp <= 0 and self.mechanic in ("undying", "reaper") and not self._undying_used:
            self._undying_used = True
            self.hp = max(1, self.max_hp // 6)
            if self.mechanic == "reaper":
                return f"💀 {self.name}: 'Der Tod betrügt nicht – ER betrügt.' – überlebt mit {self.hp} HP!"
            return f"🕯️ {self.name}: 'Was ist überhaupt Tod?' – überlebt mit {self.hp} HP!"
        return None

    def heal(self, amount):
        before = self.hp
        self.hp = min(self.max_hp, self.hp + amount)
        return self.hp - before
    
    def get_intent_text(self):
        icons = {
            "attack":       f"⚔️ {self.intent_value} Schaden",
            "heavy_attack": f"💢 {self.intent_value} Schaden (stark!)",
            "defend":       f"🛡️ {self.intent_value} Block",
            "taunt":        "😤 Verspottet dich (−2 Stärke!)",
            "spin":         "🎰 Dreht seinen Automaten…",
        }
        return icons.get(self.intent, "?")
    
    def take_damage(self, amount):
        """Gegner nimmt Schaden"""
        if self.vulnerable > 0:
            amount = int(amount * 1.5)
        if self.marked > 0 and amount > 0:
            amount += self.marked      # Markiert: pauschaler Bonus pro Treffer
        effective = max(0, amount - self.armor)
        absorbed = min(self.block, effective)
        self.block -= absorbed
        effective -= absorbed
        self.hp = max(0, self.hp - effective)
        return effective
    
    def execute_turn(self, player):
        """Führt die geplante Aktion aus, gibt Log-Text zurück"""
        result = []
        self.turn_count += 1

        # Block vom letzten Zug läuft ab (sonst sammelt er sich unsichtbar an)
        self.block = 0

        # Burn
        if self.burn > 0:
            burn_dmg = self.burn
            self.hp = max(0, self.hp - burn_dmg)
            result.append(f"{self.name} brennt! ({burn_dmg} Schaden)")
            self.burn = max(0, self.burn - 1)

        # Gift (sinkt nicht – belohnt Gift-Aufbau über mehrere Runden)
        if self.poison > 0:
            self.hp = max(0, self.hp - self.poison)
            result.append(f"☠️ {self.name} leidet unter Gift! ({self.poison} Schaden)")

        # Verhängnis: Countdown, am Ende ein massiver Selbstschlag
        if self.doom > 0:
            self.doom -= 1
            if self.doom == 0:
                boom = max(20, self.max_hp // 2)
                self.hp = max(0, self.hp - boom)
                result.append(f"💥 VERHÄNGNIS bricht über {self.name} herein! ({boom} Schaden)")

        # Status-Abbau
        if self.weakened > 0:
            self.weakened -= 1
        if self.vulnerable > 0:
            self.vulnerable -= 1
        if self.marked > 0:
            self.marked = max(0, self.marked - 1)

        # Gift/Verhängnis kann töten, bevor der Gegner handelt
        if self.hp <= 0:
            return result

        # Betäubt: überspringt den Zug komplett
        if self.stunned > 0:
            self.stunned -= 1
            result.append(f"💫 {self.name} ist betäubt und kann nicht handeln!")
            self._randomize_intent()
            return result

        # Slot-Boss: dreht seinen EIGENEN Automaten statt normalem Zug
        if self.mechanic == "slot_boss":
            result.extend(self._slot_boss_turn(player))
            self._randomize_intent()
            return result

        # Leeren-Wandler: frisst deinen Block VOR dem Schlag
        if (self.mechanic == "block_eater" and self.intent in ("attack", "heavy_attack")
                and player.block > 0):
            eaten = player.block
            player.block = 0
            result.append(f"🕳️ {self.name} verschlingt deinen Block ({eaten})!")

        def _atk_dmg(v):
            if self.weakened > 0:
                v = v // 2
            if self.frost > 0:
                v = v // 2        # Frost: halbierter Angriffsschaden
            return v

        dealt = 0
        if self.intent == "attack":
            dealt = player.take_damage(_atk_dmg(self.intent_value))
            result.append(f"{self.name} greift an! ({dealt} Schaden)")

        elif self.intent == "heavy_attack":
            dealt = player.take_damage(_atk_dmg(self.intent_value))
            result.append(f"{self.name} HAMMERSCHLAG! ({dealt} Schaden)")

        elif self.intent == "defend":
            self.block += self.intent_value
            result.append(f"{self.name} blockt! (+{self.intent_value} Block)")

        elif self.intent == "taunt":
            # Spott demoralisiert: −2 Stärke, darf ins Minus gehen (weniger Schaden)
            player.strength -= 2
            result.append(f"{self.name} verspottet dich! −2 Stärke (jetzt {player.strength:+d})")

        # ─── Einzigartige Mechaniken ───
        result.extend(self._apply_mechanic(player, dealt))

        # Frost baut nach dem Zug ab
        if self.frost > 0:
            self.frost -= 1

        # Nächste Aktion planen
        self._randomize_intent()
        return result

    def _apply_mechanic(self, player, dealt):
        """Wendet die Spezialfähigkeit des Gegners an"""
        out = []
        m = self.mechanic
        attacked = self.intent in ("attack", "heavy_attack")

        if m == "gold_thief" and attacked:
            stolen = min(player.gold, 6 + self.tier * 5)
            if stolen > 0:
                player.gold -= stolen
                out.append(f"💸 {self.name} kassiert {stolen} Gold 'Abgaben'!")

        elif m == "chili" and attacked:
            player.burn += 2
            out.append(f"🌶️ {self.name} verbrennt dich! (+2 Burn)")

        elif m == "slot_jammer":
            if random.random() < 0.5:
                self.jam_next = True
                out.append(f"🎰 {self.name} blockiert deinen Automaten! (−1 Dreh nächste Runde)")

        elif m == "chicken_army":
            # Hühnerkönig wird langsam gefährlicher – aber gedeckelt (war zu hart)
            cap = int(self._base_damage * 1.6)
            if attacked and self.damage < cap:
                self.damage += 2
                out.append(f"🐔 {self.name} ruft sein Gefolge! (Schaden steigt leicht)")

        elif m == "rig_slots":
            # Oberster Glücksprüfer: manipuliert Glück & Automat, saugt Leben
            if player.lucky > 0:
                player.lucky = 0
                out.append(f"🎲 {self.name} löscht dein Glück! (Glücksrunden → 0)")
            # Nicht jede Runde blockieren – sonst dreht man nie (war zu hart)
            if random.random() < 0.5:
                self.jam_next = True
                out.append(f"🎰 {self.name} manipuliert deinen Automaten! (−1 Dreh)")
            if dealt > 0:
                healed = self.heal(dealt // 2)
                if healed > 0:
                    out.append(f"🩸 {self.name} saugt {healed} Leben aus dir!")

        elif m == "siphon" and dealt > 0:
            healed = self.heal(max(1, dealt // 2))
            if healed > 0:
                out.append(f"🩸 {self.name} heilt sich um {healed}!")

        elif m == "venom" and attacked:
            player.poison += 2
            out.append(f"☠️ {self.name} vergiftet dich! (+2 Gift)")

        elif m == "plague" and attacked:
            player.poison += 2
            player.vulnerable += 1
            out.append(f"🦠 {self.name} infiziert dich! (+2 Gift, +1 Verwundbar)")

        elif m == "infest":
            stacks = 2 + self.turn_count // 2     # eskaliert über die Zeit
            player.poison += stacks
            out.append(f"🥚 {self.name} verseucht dich! (+{stacks} Gift)")

        elif m == "chill" and attacked:
            player.vulnerable += 2
            out.append(f"❄️ {self.name} lässt dich erstarren! (+2 Verwundbar)")

        elif m == "freeze":
            if attacked:
                player.vulnerable += 1
                out.append(f"🧊 {self.name} friert dich ein! (+1 Verwundbar)")

        elif m == "infernal":
            player.burn += 2
            if self.turn_count % 3 == 0:
                player.burn += 2
            out.append(f"🔥 {self.name} entfacht das Höllenfeuer! (+Brennen)")

        elif m == "pierce" and attacked:
            # Schattenkrähe: 3 Schaden ignorieren Block
            extra = player.take_damage(3, ignore_block=True)
            out.append(f"🪶 {self.name} durchdringt deinen Block! ({extra} ungeblockt)")

        elif m == "gambler_foe" and random.random() < 0.3:
            healed = self.heal(random.randint(3, 8))
            if healed > 0:
                out.append(f"🎲 {self.name} würfelt sich gesund! (+{healed} HP)")

        elif m == "house_edge" and attacked:
            # Bankhalter: Bonus-Schaden je nach Gold + klaut Gold
            bonus = player.gold // 40
            if bonus > 0:
                extra = player.take_damage(bonus)
                out.append(f"🏦 Das Haus kassiert: +{extra} Schaden (dein Reichtum)!")
            stolen = min(player.gold, 8)
            if stolen > 0:
                player.gold -= stolen
                out.append(f"💸 {self.name} zieht {stolen} Gold ein!")

        elif m == "spores":
            player.poison += 2
            out.append(f"🍄 {self.name} verströmt Sporen! (+2 Gift, ohne Angriff)")

        elif m == "curse_gift":
            if random.random() < 0.35:
                curse = random.choice(CURSE_DEFINITIONS)
                player.add_card_to_deck(curse)
                out.append(f"🪞 {self.name} zeigt dir dein Spiegelbild: '{curse['name']}' liegt in deinem Deck!")

        elif m == "luck_eater":
            if player.lucky > 0:
                player.lucky -= 1
                healed = self.heal(6)
                out.append(f"👻 {self.name} frisst eine Glücksrunde! (+{healed} HP für ihn)")

        elif m == "reaper":
            # Croupier des Todes: teilt eine Schicksalskarte aus (haerter als Fortuna)
            fate = random.choice(["scythe", "poison", "drain", "double"])
            if fate == "scythe":
                cut = player.take_damage(max(1, int(self.damage * 0.6)))
                out.append(f"☠️ {self.name} schwingt die Sense! ({cut} Extra-Schaden)")
            elif fate == "poison":
                player.poison += 4
                out.append("☠️ Todeshauch: +4 Gift auf dich!")
            elif fate == "drain":
                healed = self.heal(14)
                out.append(f"🩸 {self.name} erntet Leben (+{healed} HP für ihn)!")
            else:
                extra = player.take_damage(max(1, self.damage // 2))
                out.append(f"🃏 Schicksalskarte: DOPPELSCHLAG! ({extra} Extra-Schaden)")

        elif m == "fortuna":
            wheel = random.choice(["poison", "steal", "heal", "double"])
            if wheel == "poison":
                player.poison += 3
                out.append("🎡 Schicksalsrad: GIFT! (+3 Gift auf dich)")
            elif wheel == "steal":
                stolen = min(player.gold, 10)
                if stolen > 0:
                    player.gold -= stolen
                    out.append(f"🎡 Schicksalsrad: DIEBSTAHL! (−{stolen} Gold)")
            elif wheel == "heal":
                healed = self.heal(12)
                out.append(f"🎡 Schicksalsrad: HEILUNG! (+{healed} HP für sie)")
            else:
                extra = player.take_damage(max(1, self.damage // 2))
                out.append(f"🎡 Schicksalsrad: DOPPELSCHLAG! ({extra} Extra-Schaden)")

        elif m == "mirror_boss" and attacked:
            # Spiegel-Ich: Bonus-Schaden skaliert mit DEINER Macht
            bonus = player.strength + player.block // 3 + len(player.relics)
            if bonus > 0:
                extra = player.take_damage(bonus)
                out.append(f"🪞 {self.name} spiegelt deine Macht! (+{extra} Schaden)")

        return out

    # ─── Slot-Boss: dreht seinen eigenen 3-Walzen-Automaten ───
    SLOT_BOSS_FACES = ["SKULL", "SKULL", "HEART", "TRAP", "SHIELD", "MONEY", "FIRE", "DICE"]

    def _slot_boss_turn(self, player):
        """Der Jackpot-Automat dreht; das Ergebnis bestimmt die Aktion.
        Die gewürfelten Symbole landen in self.last_slot (für die UI-Anzeige)."""
        names = [random.choice(self.SLOT_BOSS_FACES) for _ in range(3)]
        self.last_slot = names
        self.last_slot_timer = 2.2
        out = [f"🎰 {self.name} dreht: {' '.join(SLOT_BOSS_EMOJI.get(n, '?') for n in names)}"]
        triple = len(set(names)) == 1
        dmg = self.damage
        if triple:
            sym = names[0]
            if sym == "SKULL":
                hit = player.take_damage(int(dmg * 2.4))
                out.append(f"💀💀💀 VOLLTREFFER! {hit} Schaden!")
            elif sym == "HEART":
                h = self.heal(int(self.max_hp * 0.25))
                out.append(f"❤️❤️❤️ Der Automat heilt sich um {h}!")
            elif sym == "TRAP":
                self.hp = max(0, self.hp - int(self.max_hp * 0.12))
                out.append("🪤🪤🪤 FEHLZÜNDUNG! Der Automat schädigt sich selbst!")
            elif sym == "SHIELD":
                self.block += dmg * 2
                out.append(f"🛡️🛡️🛡️ Bunker-Modus! (+{dmg*2} Block)")
            elif sym == "MONEY":
                stolen = min(player.gold, 30)
                player.gold -= stolen
                hit = player.take_damage(dmg)
                out.append(f"💰💰💰 ABZOCKE! −{stolen} Gold und {hit} Schaden!")
            else:
                hit = player.take_damage(int(dmg * 1.8)); player.burn += 3
                out.append(f"🔥🔥🔥 ÜBERHITZUNG! {hit} Schaden + 3 Brennen!")
            return out
        # Kein Drilling: jedes Symbol wirkt einzeln (mild)
        for sym in names:
            if sym == "SKULL":
                player.take_damage(max(1, dmg // 2))
            elif sym == "FIRE":
                player.take_damage(max(1, dmg // 3)); player.burn += 1
            elif sym == "HEART":
                self.heal(8)
            elif sym == "SHIELD":
                self.block += dmg // 2
            elif sym == "MONEY":
                s = min(player.gold, 8); player.gold -= s
            elif sym == "TRAP":
                self.hp = max(0, self.hp - 4)
            # DICE: nichts (Glück gehabt)
        out.append("Die Walzen rattern – gemischtes Ergebnis.")
        return out

    def get_gold_reward(self):
        return random.randint(*self.gold_reward)
    
    def is_alive(self):
        return self.hp > 0
