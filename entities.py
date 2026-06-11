"""Kern-Spielklassen: Spieler, Gegner, Karten"""

import random
import copy
from constants import *


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


class Player:
    """Der Spieler mit HP, Deck, Hand, Gold und Status"""
    
    def __init__(self):
        self.max_hp = PLAYER_MAX_HP
        self.hp = PLAYER_MAX_HP
        self.gold = PLAYER_START_GOLD
        self.block = 0
        self.energy = PLAYER_ENERGY_PER_TURN
        self.max_energy = PLAYER_ENERGY_PER_TURN
        
        # Status-Effekte
        self.burn = 0          # Schaden pro Runde
        self.strength = 0      # Schadensbonus
        self.lucky = 0         # Slot-Bonus-Runden
        self.shield_up = False # Doppel-Block diese Runde
        self.reflect = False   # Reflektiert nächsten Schaden
        self.coin_rain_active = False  # +Gold je gespielter Karte
        self.next_free_card = False    # Nächste Karte kostet 0 (Schattenschritt)
        self._total_damage_taken = 0   # Gesamtschaden über den Run (für Vergeltung)
        
        # Deck-System
        self.deck = []
        self.hand = []
        self.discard = []

        # Relikte (permanente passive Boni)
        self.relics = []   # Liste von Relikt-Dicts
        
        # Statistiken
        self.damage_dealt = 0
        self.gold_earned = 0
        self.slots_spun = 0
        self.chickens_summoned = 0
        self.enemies_defeated = 0
        
        # Slot-Spins diese Runde (Double/Triple Spin)
        self.bonus_spins = 0
        
        self._build_starter_deck()
    
    def _build_starter_deck(self):
        """Startdeck mit 10 Karten"""
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
    
    def discard_hand(self):
        """Wirft alle Handkarten ab"""
        self.discard.extend(self.hand)
        self.hand = []
    
    def start_turn(self):
        """Rundenstart: Energie auffüllen, Karten nachziehen (Block bleibt erhalten!)"""
        self.energy = self.max_energy
        self.bonus_spins = 0
        self.reflect = False
        self.coin_rain_active = False
        self.next_free_card = False
        if self.shield_up:
            self.shield_up = False
        # Burn-Schaden
        if self.burn > 0:
            self.take_damage(self.burn, ignore_block=True)
            self.burn = max(0, self.burn - 1)
        # Nur nachziehen (ungespielte Karten bleiben in der Hand)
        self.draw_hand()
    
    def take_damage(self, amount, ignore_block=False):
        """Nimmt Schaden, reduziert durch Block"""
        if not ignore_block:
            absorbed = min(self.block, amount)
            self.block -= absorbed
            amount -= absorbed
        self.hp = max(0, self.hp - amount)
        if amount > 0:
            self._total_damage_taken += amount
        return amount  # tatsächlicher Schaden
    
    def heal_hp(self, amount):
        """Heilt HP bis zum Maximum"""
        old = self.hp
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

        # Status
        self.burn = 0
        self.weakened = 0   # Runden mit halbiertem Schaden
        
        # KI: Was plant der Gegner diese Runde?
        self.intent = "attack"
        self.intent_value = self.damage
        self._randomize_intent()
    
    def _randomize_intent(self):
        """Bestimmt die nächste Aktion des Gegners"""
        roll = random.random()
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
                self.intent_value = 8
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
        else:
            if roll < 0.65:
                self.intent = "attack"
                self.intent_value = self.damage
            elif roll < 0.80:
                self.intent = "defend"
                self.intent_value = 6
            elif roll < 0.92:
                self.intent = "taunt"
                self.intent_value = 0
            else:
                self.intent = "heavy_attack"
                self.intent_value = int(self.damage * 1.5)

    def try_undying(self):
        """Lich-Mechanik: einmal pro Kampf den Tod überleben. Gibt Log oder None."""
        if self.hp <= 0 and self.mechanic == "undying" and not self._undying_used:
            self._undying_used = True
            self.hp = max(1, self.max_hp // 6)
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
            "taunt":        "😤 Verspottet dich (tut nichts)",
        }
        return icons.get(self.intent, "?")
    
    def take_damage(self, amount):
        """Gegner nimmt Schaden"""
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

        # Schwächungs-Abbau
        if self.weakened > 0:
            self.weakened -= 1

        dealt = 0
        if self.intent == "attack":
            dmg = self.intent_value
            if self.weakened > 0:
                dmg = dmg // 2
            dealt = player.take_damage(dmg)
            result.append(f"{self.name} greift an! ({dealt} Schaden)")

        elif self.intent == "heavy_attack":
            dmg = self.intent_value
            if self.weakened > 0:
                dmg = dmg // 2
            dealt = player.take_damage(dmg)
            result.append(f"{self.name} HAMMERSCHLAG! ({dealt} Schaden)")

        elif self.intent == "defend":
            self.block += self.intent_value
            result.append(f"{self.name} blockt! (+{self.intent_value} Block)")

        elif self.intent == "taunt":
            result.append(f"{self.name}: 'Du kannst mich nicht besiegen!' (leer)")

        # ─── Einzigartige Mechaniken ───
        result.extend(self._apply_mechanic(player, dealt))

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

        return out
    
    def get_gold_reward(self):
        return random.randint(*self.gold_reward)
    
    def is_alive(self):
        return self.hp > 0
