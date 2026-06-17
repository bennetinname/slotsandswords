"""Slot-Maschinen-System: Reel-Animation, Ergebnisse, Effekte"""

import pygame
import random
import time
from constants import *
import assets


def _symbol_img(sym, size):
    """Slot-Symbol-Sprite (oder None, dann Emoji-Fallback)"""
    return assets.scaled("slots", sym["name"].lower(), size, size)


def weighted_choice(symbols):
    """Wählt ein Symbol basierend auf Gewichtungen"""
    total = sum(s["weight"] for s in symbols)
    r = random.uniform(0, total)
    cumulative = 0
    for s in symbols:
        cumulative += s["weight"]
        if r <= cumulative:
            return s
    return symbols[-1]


class SlotReel:
    """Eine einzelne Slot-Walze mit Animation"""
    
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
        self.current_symbol = random.choice(SLOT_SYMBOLS)
        self.spinning = False
        self.spin_start = 0
        self.spin_duration = 0
        self.target_symbol = None
        self.spin_offset = 0.0  # 0..1 scroll-Offset
        self.display_symbols = []  # Symbole zum Rendern während Spin
        self._generate_display_symbols()
    
    def _generate_display_symbols(self):
        self.display_symbols = [random.choice(SLOT_SYMBOLS) for _ in range(5)]
        if self.current_symbol:
            self.display_symbols[2] = self.current_symbol
    
    def start_spin(self, duration, target=None):
        """Startet die Drehanimation"""
        self.spinning = True
        self.spin_start = time.time()
        self.spin_duration = duration
        self.target_symbol = target or weighted_choice(SLOT_SYMBOLS)
        self.spin_offset = 0.0
        self._generate_display_symbols()
    
    def update(self):
        """Aktualisiert den Animationszustand"""
        if not self.spinning:
            return False
        
        elapsed = time.time() - self.spin_start
        progress = min(1.0, elapsed / self.spin_duration)
        
        # Zufällig rotierende Offset-Animation
        speed = 8.0 * (1.0 - progress * 0.7)  # Abbremsen am Ende
        self.spin_offset = (self.spin_offset + speed * 0.016) % 1.0
        
        if progress >= 1.0:
            self.spinning = False
            self.current_symbol = self.target_symbol
            self.display_symbols[2] = self.current_symbol
            return True  # Fertig
        
        # Neue Zufallssymbole während Spin
        if random.random() < 0.15:
            self._generate_display_symbols()
            self.display_symbols[2] = self.target_symbol
        
        return False
    
    def draw(self, screen, font_large, font_small):
        """Zeichnet die Walze"""
        # Walzen-Hintergrund
        pygame.draw.rect(screen, SLOT_REEL, (self.x, self.y, self.width, self.height), border_radius=8)
        pygame.draw.rect(screen, CARD_BORDER, (self.x, self.y, self.width, self.height), 2, border_radius=8)
        
        size = min(self.width - 10, 72)
        if self.spinning:
            # Animiertes Scroll durch Symbole
            symbol_h = self.height // 3
            for i in range(5):
                idx = int((self.spin_offset * 5 + i) % len(self.display_symbols))
                sym = self.display_symbols[idx % len(self.display_symbols)]
                sy = self.y + (i - 1) * symbol_h + int(self.spin_offset * symbol_h) - symbol_h
                if self.y - 5 <= sy <= self.y + self.height + 5:
                    cy = sy + symbol_h // 2
                    img = _symbol_img(sym, size)
                    if img:
                        screen.blit(img, (self.x + self.width//2 - img.get_width()//2,
                                          cy - img.get_height()//2))
                    else:
                        txt = font_large.render(sym["emoji"], True, WHITE)
                        screen.blit(txt, (self.x + self.width//2 - txt.get_width()//2,
                                          cy - txt.get_height()//2))
            # Motion-Blur-Overlay
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((20, 15, 35, 120))
            screen.blit(overlay, (self.x, self.y))
        else:
            # Stehendes Symbol (groß, zentriert)
            sym = self.current_symbol
            cx = self.x + self.width // 2
            cy = self.y + self.height // 2
            img = _symbol_img(sym, size)
            if img:
                screen.blit(img, (cx - img.get_width()//2, cy - img.get_height()//2))
            else:
                txt = font_large.render(sym["emoji"], True, WHITE)
                screen.blit(txt, (cx - txt.get_width()//2, cy - txt.get_height()//2))
        
        # Highlight-Linie in der Mitte
        mid_y = self.y + self.height // 2
        pygame.draw.line(screen, GOLD, (self.x + 4, mid_y - 18), (self.x + self.width - 4, mid_y - 18), 1)
        pygame.draw.line(screen, GOLD, (self.x + 4, mid_y + 20), (self.x + self.width - 4, mid_y + 20), 1)


class SlotMachine:
    """Drei-Walzen-Spielautomat mit Effektauswertung"""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 340
        self.height = 200

        # Cabinet-Sprite (rahmt die Walzen) falls vorhanden – sonst Procedural
        self.cabinet = assets.has("ui", "slot_cabinet")
        if self.cabinet:
            self.cab_w, self.cab_h = 277, 223
            self.cab_x = x + self.width // 2 - self.cab_w // 2
            self.cab_y = y - 6
            # Fenster-Positionen (native Cabinet-Koordinaten) -> Walzen
            windows = [(35, 83), (99, 83), (163, 83)]
            reel_w, reel_h = 55, 104
            self.reels = [
                SlotReel(self.cab_x + wx, self.cab_y + wy, reel_w, reel_h)
                for (wx, wy) in windows
            ]
        else:
            reel_w = 90
            reel_h = 110
            spacing = 15
            start_x = x + 20
            reel_y = y + 45
            self.reels = [
                SlotReel(start_x + i * (reel_w + spacing), reel_y, reel_w, reel_h)
                for i in range(3)
            ]
        
        self.spinning = False
        self.results = []          # [symbol1, symbol2, symbol3]
        self.effects = []          # Texte der Effekte
        self.spin_complete = False
        self._reel_done = [False, False, False]
        self.glow_timer = 0.0
        self.lucky_spin = False      # war der laufende/letzte Dreh ein Glücksdreh?
    
    def spin(self, lucky_bonus=False, time_scale=1.0, targets=None,
             rig_negatives=False, force_wild=False, force_triple=False):
        """Startet den Spin aller drei Walzen. `targets` (Liste von Symbol-Dicts)
        erzwingt das Ergebnis (für den Slot-Modus). rig_negatives/force_wild =
        Relikt-Effekte (Gezinkter Automat / Walzen-Joker)."""
        self.spinning = True
        self.spin_complete = False
        self._reel_done = [False, False, False]
        self.results = []
        self.effects = []

        # Walzen starten mit leicht unterschiedlichen Dauern (Spannung!)
        durations = [d * time_scale for d in (0.9, 1.2, 1.6)]
        if targets is None:
            targets = [weighted_choice(SLOT_SYMBOLS) for _ in range(3)]

        # Glücksdreh (v1.17 aufgewertet): Negativ-Symbole werden unterdrückt,
        # und jede Walze hat eine hohe Chance auf ein GUTES Symbol.
        # Gezinkter Automat: Negativ-Symbole 50% seltener
        if rig_negatives:
            safe = [s for s in SLOT_SYMBOLS if s["name"] not in SLOT_NEGATIVE]
            for i in range(3):
                if targets[i]["name"] in SLOT_NEGATIVE and random.random() < 0.5:
                    targets[i] = random.choice(safe)

        self.lucky_spin = bool(lucky_bonus)
        if lucky_bonus:
            good = [s for s in SLOT_SYMBOLS if s["name"] in GOOD_SYMBOLS]
            safe = [s for s in SLOT_SYMBOLS if s["name"] not in SLOT_NEGATIVE]
            for i in range(3):
                # 1) Negativ-Symbole gibt's im Glücksdreh nicht
                if targets[i]["name"] in SLOT_NEGATIVE:
                    targets[i] = random.choice(safe)
                # 2) starker Bias auf gute Symbole
                if random.random() < 0.55:
                    targets[i] = random.choice(good)

        # Walzen-Joker: ein garantiertes WILD
        if force_wild:
            wild = next((s for s in SLOT_SYMBOLS if s["name"] == "WILD"), None)
            if wild:
                targets[random.randint(0, 2)] = wild

        # Jackpot erzwingen: garantierter Drilling (nie ein Negativ-Symbol)
        if force_triple:
            pool = [s for s in SLOT_SYMBOLS if s["name"] not in SLOT_NEGATIVE]
            sym = weighted_choice(pool)
            targets = [sym, sym, sym]

        for i, reel in enumerate(self.reels):
            reel.start_spin(durations[i], targets[i])
    
    def update(self):
        """Aktualisiert alle Walzen, gibt True zurück wenn fertig"""
        all_done = True
        for i, reel in enumerate(self.reels):
            was_spinning = reel.spinning
            reel.update()
            if was_spinning and not reel.spinning and not self._reel_done[i]:
                self._reel_done[i] = True
            if reel.spinning:
                all_done = False
        
        if all_done and self.spinning:
            self.spinning = False
            self.spin_complete = True
            self.results = [r.current_symbol for r in self.reels]
            self.glow_timer = 2.0
            return True
        
        self.glow_timer = max(0, self.glow_timer - 0.016)
        return False
    
    @staticmethod
    def _resolve_wild(names):
        """WILD zählt als jedes Symbol: ersetzt jedes WILD durch das häufigste
        echte Symbol (maximiert Paare/Drillinge). Alle WILD -> Jackpot (DIAMOND)."""
        if "WILD" not in names:
            return names
        from collections import Counter
        non = [n for n in names if n != "WILD"]
        if not non:
            return ["DIAMOND", "DIAMOND", "DIAMOND"]
        most = Counter(non).most_common(1)[0][0]
        return [most if n == "WILD" else n for n in names]

    def evaluate(self, player, enemy):
        """Wertet Slot-Ergebnisse aus, gibt Liste von Effekt-Strings zurück"""
        if not self.results:
            return []

        effects = []
        names = self._resolve_wild([r["name"] for r in self.results])
        if names != [r["name"] for r in self.results]:
            effects.append("🎰 WILD verwandelt sich!")

        # Dreier-Kombos (erste prüfen)
        if len(set(names)) == 1:
            sym = names[0]
            effects.extend(self._triple_combo(sym, player, enemy))
        else:
            # Einzel-Effekte jedes Symbols (aufgelöste Namen, WILD bereits ersetzt)
            for nm in names:
                eff = self._single_effect(nm, player, enemy)
                if eff:
                    effects.append(eff)
            
            # Paare als Bonus
            from collections import Counter
            counts = Counter(names)
            for name, count in counts.items():
                if count == 2:
                    effects.append(self._pair_bonus(name, player, enemy))

            # Cross-Symbol-Synergien (verschiedene Symbole, die zusammenpassen)
            effects.extend(self._synergies(names, player, enemy))

        self.effects = [e for e in effects if e]
        return self.effects
    
    def _triple_combo(self, sym, player, enemy):
        """Dreier-Treffer: große Effekte!"""
        effects = []
        if sym == "SKULL":
            dmg = 35
            actual = enemy.take_damage(dmg + player.strength)
            effects.append(f"💀💀💀 DREIFACHSCHÄDEL! {actual} MASSIVSCHADEN!")
        elif sym == "MONEY":
            gold = 30
            player.add_gold(gold)
            effects.append(f"💰💰💰 GOLDMINE! +{gold} Gold! ITS RAINING MONEY!")
        elif sym == "HEART":
            healed = player.heal_hp(30)
            effects.append(f"❤️❤️❤️ VOLLHEILUNG! +{healed} HP!")
        elif sym == "FIRE":
            dmg = 50
            actual = enemy.take_damage(dmg + player.strength)
            enemy.burn += 3
            effects.append(f"🔥🔥🔥 INFERNO! {actual} Schaden + 3 Brennen!")
        elif sym == "CLOVER":
            player.lucky += 3
            player.add_gold(20)
            healed = player.heal_hp(15)
            effects.append(f"🍀🍀🍀 IRRES GLÜCK! +3 Glücksrunden, +20 Gold, +{healed} HP!")
        elif sym == "CHICKEN":
            # Hühner-Jackpot: komplett zufällig
            import random
            n = random.randint(3, 7)
            dmg = n * 8
            actual = enemy.take_damage(dmg)
            player.chickens_summoned += n
            effects.append(f"🐔🐔🐔 HÜHNER-JACKPOT! {n} Hühner! {actual} Schaden! 🐔🐔🐔")
        elif sym == "DICE":
            # Chaos hoch drei
            effects.extend(self._chaos_effect(player, enemy, multiplier=3))
        elif sym == "STAR":
            player.strength += 3
            effects.append("⭐⭐⭐ STERNENPOWER! +3 Stärke (diesen Kampf)!")
        elif sym == "BOMB":
            dmg = 40
            self_dmg = 10
            actual = enemy.take_damage(dmg + player.strength)
            player.take_damage(self_dmg, ignore_block=True)
            effects.append(f"💣💣💣 DREIFACHBOMBE! {actual} Schaden! {self_dmg} Selbstschaden!")
        elif sym == "CROWN":
            player.max_hp += 10
            player.hp += 10
            player.add_gold(25)
            effects.append("👑👑👑 TRIPLE CROWN! +10 Max HP, +25 Gold!")
        elif sym == "BEER":
            healed = player.heal_hp(20)
            enemy.weakened += 2
            effects.append(f"🍺🍺🍺 BIERGARTEN! +{healed} HP! Gegner 2 Runden geschwächt!")
        elif sym == "VORTEX":
            # Tauscht HP
            p_hp = player.hp
            e_hp = enemy.hp
            player.hp = min(e_hp, player.max_hp)
            enemy.hp = e_hp  # Bleibt gleich... wait
            actual_dmg = max(0, p_hp - e_hp)
            enemy.hp = max(1, enemy.hp - actual_dmg)
            effects.append("🌀🌀🌀 HP-VORTEX! Chaos! Schmerz! Freude!")
        elif sym == "LIGHTNING":
            actual = enemy.take_damage(35 + player.strength)
            player.energy_next_turn = getattr(player, "energy_next_turn", 0) + 2
            effects.append(f"⚡⚡⚡ GEWITTERSTURM! {actual} Schaden, +2 Energie nächste Runde!")
        elif sym == "SHIELD":
            player.block += 30
            effects.append("🛡️🛡️🛡️ FESTUNG! +30 Block!")
        elif sym == "TARGET":
            actual = enemy.take_damage((25 + player.strength) * 2)
            effects.append(f"🎯🎯🎯 PERFEKTER TREFFER! {actual} KRITSCHADEN!")
        elif sym == "CHERRY":
            player.add_gold(15)
            healed = player.heal_hp(15)
            enemy.take_damage(15)
            effects.append(f"🍒🍒🍒 KIRSCHEN! +15 Gold, +{healed} HP, 15 Schaden!")
        elif sym == "DIAMOND":
            player.add_gold(50)
            player.strength += 2
            effects.append("💎💎💎 DIAMANT-JACKPOT! +50 Gold, +2 Stärke!")
        elif sym == "SNAKE":
            enemy.burn += 5
            actual = enemy.take_damage(15)
            effects.append(f"🐍🐍🐍 GIFTNEST! {actual} Schaden + 5 Gift-Stacks!")
        elif sym == "MOON":
            missing = player.max_hp - player.hp
            healed = player.heal_hp(missing)
            effects.append(f"🌙🌙🌙 VOLLMOND! Komplett geheilt (+{healed} HP)!")
        elif sym == "CLOWN":
            effects.append("🤡🤡🤡 ZIRKUS! Pure Anarchie folgt:")
            effects.extend(self._chaos_effect(player, enemy, multiplier=2))
        elif sym == "BELL":
            player.add_gold(18); healed = player.heal_hp(15)
            effects.append(f"🔔🔔🔔 GLOCKENSPIEL! +18 Gold, +{healed} HP!")
        elif sym == "GEM":
            player.add_gold(60)
            effects.append("💍💍💍 EDELSTEIN-JACKPOT! +60 Gold!")
        elif sym == "TRAP":
            dmg = 28
            player.take_damage(dmg, ignore_block=True)
            effects.append(f"🪤🪤🪤 TODESFALLE! {dmg} Selbstschaden – aua!")
        elif sym == "PIT":
            lost = min(player.gold, 40)
            player.gold -= lost
            player.energy_next_turn = getattr(player, "energy_next_turn", 0) - 1
            effects.append(f"🕳️🕳️🕳️ ABGRUND! −{lost} Gold und −1 Energie nächste Runde!")
        elif sym == "CURSE":
            player.block = 0
            player.vulnerable += 3
            effects.append("🧿🧿🧿 DREIFACHER FLUCH! Block weg, +3 Verwundbar!")
        else:
            effects.append(f"TRIPLE {sym}! Etwas Seltsames passiert...")
        return effects
    
    def _single_effect(self, sym, player, enemy):
        """Einzelner Symbol-Effekt"""
        if sym == "SKULL":
            dmg = random.randint(8, 16) + player.strength
            actual = enemy.take_damage(dmg)
            return f"💀 {actual} Schaden"
        elif sym == "MONEY":
            gold = random.randint(5, 12)
            player.add_gold(gold)
            return f"💰 +{gold} Gold"
        elif sym == "HEART":
            healed = player.heal_hp(random.randint(6, 14))
            return f"❤️ +{healed} HP" if healed > 0 else None
        elif sym == "FIRE":
            dmg = random.randint(10, 20) + player.strength
            actual = enemy.take_damage(dmg)
            return f"🔥 {actual} Feuerschaden"
        elif sym == "CLOVER":
            if random.random() < 0.5:
                player.lucky += 1
                return "🍀 +1 Glücksrunde!"
            else:
                gold = random.randint(3, 8)
                player.add_gold(gold)
                return f"🍀 Kleines Glück: +{gold} Gold"
        elif sym == "CHICKEN":
            return self._chicken_effect(player, enemy)
        elif sym == "DICE":
            effs = self._chaos_effect(player, enemy)
            return effs[0] if effs else None
        elif sym == "STAR":
            if random.random() < 0.3:
                player.strength += 1
                return "⭐ +1 Stärke!"
            else:
                dmg = random.randint(5, 12) + player.strength
                actual = enemy.take_damage(dmg)
                return f"⭐ Sternenstrahl: {actual} Schaden"
        elif sym == "BOMB":
            dmg = random.randint(15, 25) + player.strength
            self_dmg = random.randint(3, 8)
            actual = enemy.take_damage(dmg)
            player.take_damage(self_dmg, ignore_block=True)
            return f"💣 BOOM! {actual} Schaden, {self_dmg} Selbstschaden"
        elif sym == "CROWN":
            gold = random.randint(10, 18)
            player.add_gold(gold)
            return f"👑 Königsbonus: +{gold} Gold"
        elif sym == "BEER":
            healed = player.heal_hp(random.randint(4, 10))
            return f"🍺 Schluck Bier: +{healed} HP"
        elif sym == "VORTEX":
            if random.random() < 0.5:
                dmg = random.randint(5, 18)
                actual = enemy.take_damage(dmg)
                return f"🌀 Wirbelschaden: {actual}"
            else:
                return "🌀 Nichts passiert... oder doch?"
        elif sym == "LIGHTNING":
            dmg = random.randint(8, 16) + player.strength
            actual = enemy.take_damage(dmg)
            if random.random() < 0.4:
                player.energy_next_turn = getattr(player, "energy_next_turn", 0) + 1
                return f"⚡ Blitz: {actual} Schaden, +1 Energie nächste Runde!"
            return f"⚡ Blitz: {actual} Schaden"
        elif sym == "SHIELD":
            player.block += random.randint(6, 12)
            return "🛡️ Schutzschild: +Block"
        elif sym == "TARGET":
            dmg = (random.randint(6, 12) + player.strength) * 2
            actual = enemy.take_damage(dmg)
            return f"🎯 Kritischer Treffer: {actual} Schaden!"
        elif sym == "CHERRY":
            roll = random.random()
            if roll < 0.4:
                player.add_gold(random.randint(4, 9))
                return "🍒 Kirsche: etwas Gold"
            elif roll < 0.7:
                player.heal_hp(random.randint(4, 9))
                return "🍒 Kirsche: etwas Heilung"
            else:
                enemy.take_damage(random.randint(4, 9))
                return "🍒 Kirsche: etwas Schaden"
        elif sym == "DIAMOND":
            player.add_gold(random.randint(15, 30))
            return "💎 Diamant: viel Gold!"
        elif sym == "SNAKE":
            if random.random() < 0.7:
                enemy.burn += 2
                return "🐍 Schlange: Gegner vergiftet (+2 Burn)"
            else:
                player.take_damage(random.randint(3, 7), ignore_block=True)
                return "🐍 Schlange beißt DICH. Pech."
        elif sym == "MOON":
            missing = player.max_hp - player.hp
            healed = player.heal_hp(missing // 2)
            return f"🌙 Mondlicht: +{healed} HP" if healed > 0 else "🌙 Mondlicht (volle HP)"
        elif sym == "CLOWN":
            effs = self._chaos_effect(player, enemy)
            return "🤡 " + (effs[0] if effs else "Clown stolpert weg.")
        elif sym == "BELL":
            player.add_gold(random.randint(3, 7))
            player.heal_hp(random.randint(3, 6))
            return "🔔 Glocke: etwas Gold & Heilung"
        elif sym == "GEM":
            player.add_gold(random.randint(12, 22))
            return "💍 Edelstein: Gold"
        # ─── NEGATIV-Symbole: einzeln spürbar ───
        elif sym == "TRAP":
            dmg = random.randint(6, 11)
            player.take_damage(dmg, ignore_block=True)
            return f"🪤 Falle! {dmg} Selbstschaden"
        elif sym == "PIT":
            if player.gold >= 5 and random.random() < 0.6:
                lost = min(player.gold, random.randint(8, 16))
                player.gold -= lost
                return f"🕳️ Pechloch: −{lost} Gold"
            player.energy_next_turn = getattr(player, "energy_next_turn", 0) - 1
            return "🕳️ Pechloch: −1 Energie nächste Runde"
        elif sym == "CURSE":
            if player.block > 0:
                player.block = player.block // 2
                return "🧿 Fluch: halber Block"
            player.vulnerable += 1
            return "🧿 Fluch: +1 Verwundbar"
        return None

    def _pair_bonus(self, sym, player, enemy):
        """Paar-Bonus (schwächer als Triple)"""
        if sym == "SKULL":
            dmg = 10 + player.strength
            enemy.take_damage(dmg)
            return f"💀💀 Paar: {dmg} Bonus-Schaden!"
        elif sym == "MONEY":
            player.add_gold(8)
            return "💰💰 Paar: +8 Bonus-Gold!"
        elif sym == "HEART":
            player.heal_hp(8)
            return "❤️❤️ Paar: +8 Bonus-HP!"
        elif sym == "FIRE":
            enemy.burn += 2
            return "🔥🔥 Paar: Gegner brennt! (+2 Burn)"
        elif sym == "SNAKE":
            enemy.poison += 4
            return "🐍🐍 GIFT-EXPLOSION! +4 Gift!"
        elif sym == "SHIELD":
            player.block += 12
            return "🛡️🛡️ Paar: +12 Block!"
        elif sym == "LIGHTNING":
            enemy.take_damage(12 + player.strength)
            player.energy_next_turn = getattr(player, "energy_next_turn", 0) + 1
            return "⚡⚡ Paar: 12 Schaden, +1 Energie nächste Runde!"
        elif sym == "TARGET":
            enemy.vulnerable += 2
            return "🎯🎯 Paar: Gegner 2 Runden verwundbar!"
        elif sym == "STAR":
            player.strength += 1
            return "⭐⭐ Paar: +1 Stärke!"
        elif sym == "DIAMOND":
            player.add_gold(20)
            return "💎💎 Paar: +20 Gold!"
        elif sym == "BOMB":
            enemy.take_damage(18 + player.strength)
            return "💣💣 Paar: 18 Bonus-Schaden!"
        elif sym == "CHERRY":
            player.add_gold(6)
            player.heal_hp(6)
            return "🍒🍒 Paar: +6 Gold, +6 HP!"
        elif sym == "CLOVER":
            player.lucky += 1
            return "🍀🍀 Paar: +1 Glücksrunde!"
        elif sym == "BEER":
            enemy.weakened += 1
            return "🍺🍺 Paar: Gegner geschwächt!"
        elif sym == "CHICKEN":
            return self._chicken_effect(player, enemy)
        elif sym == "BELL":
            player.add_gold(10); player.heal_hp(8)
            return "🔔🔔 Paar: +10 Gold, +8 HP!"
        elif sym == "GEM":
            player.add_gold(35)
            return "💍💍 Paar: +35 Gold!"
        # ─── NEGATIV-Paare: deutlich übler als einzeln ───
        elif sym == "TRAP":
            dmg = random.randint(16, 24)
            player.take_damage(dmg, ignore_block=True)
            return f"🪤🪤 DOPPELFALLE! {dmg} Selbstschaden!"
        elif sym == "PIT":
            lost = min(player.gold, random.randint(20, 35))
            player.gold -= lost
            player.energy = max(0, player.energy - 1)
            return f"🕳️🕳️ TIEFER FALL! −{lost} Gold, −1 Energie!"
        elif sym == "CURSE":
            player.block = 0
            player.vulnerable += 2
            return "🧿🧿 DOPPELFLUCH! Block weg, +2 Verwundbar!"
        return None

    # ── Cross-Symbol-Synergien: bestimmte Symbol-PAARE verschiedener Sorten
    #    geben einen Extra-Bonus (auch ohne Drilling/Paar). Belohnt clevere Builds.
    SYNERGIES = [
        ("SNAKE", "FIRE",     "🐍🔥 BRANDGIFT", "Gift trifft Flamme"),
        ("TARGET", "BOMB",    "🎯💣 PRÄZISIONSSCHLAG", "markiert & gesprengt"),
        ("LIGHTNING", "DIAMOND", "⚡💎 ÜBERLADUNG", "Energie aus Kristall"),
        ("CLOVER", "DICE",    "🍀🎲 SCHICKSALSGLÜCK", "das Glück würfelt mit"),
        ("HEART", "MOON",     "❤️🌙 LEBENSQUELL", "Mondlicht heilt"),
        ("SHIELD", "STAR",    "🛡️⭐ HELDENMUT", "Schild & Stärke"),
        ("MONEY", "CROWN",    "💰👑 REICHTUM", "Gold ruft Gold"),
        ("SKULL", "TARGET",   "💀🎯 TODESURTEIL", "ins Schwarze"),
    ]

    def _synergies(self, names, player, enemy):
        """Bonus-Effekte, wenn zwei bestimmte VERSCHIEDENE Symbole zusammen liegen."""
        out = []
        present = set(names)
        for a, b, title, _flavor in self.SYNERGIES:
            if a in present and b in present:
                out.append(self._apply_synergy(a, b, title, player, enemy))
        return [o for o in out if o]

    def _apply_synergy(self, a, b, title, player, enemy):
        combo = frozenset((a, b))
        if combo == frozenset(("SNAKE", "FIRE")):
            enemy.poison += 3
            enemy.burn += 2
            return f"{title}: +3 Gift & +2 Burn!"
        if combo == frozenset(("TARGET", "BOMB")):
            dmg = enemy.take_damage((20 + player.strength) * (2 if enemy.vulnerable > 0 else 1))
            enemy.vulnerable += 1
            return f"{title}: {dmg} Schaden, +1 Verwundbar!"
        if combo == frozenset(("LIGHTNING", "DIAMOND")):
            player.energy_next_turn = getattr(player, "energy_next_turn", 0) + 2
            player.add_gold(20)
            return f"{title}: +2 Energie nächste Runde, +20 Gold!"
        if combo == frozenset(("CLOVER", "DICE")):
            player.lucky += 2
            return f"{title}: +2 Glücksrunden!"
        if combo == frozenset(("HEART", "MOON")):
            healed = player.heal_hp(max(12, (player.max_hp - player.hp) // 2))
            return f"{title}: +{healed} HP!"
        if combo == frozenset(("SHIELD", "STAR")):
            player.block += 15
            player.strength += 1
            return f"{title}: +15 Block, +1 Stärke!"
        if combo == frozenset(("MONEY", "CROWN")):
            bonus = 15 + player.gold // 20
            player.add_gold(bonus)
            return f"{title}: +{bonus} Gold!"
        if combo == frozenset(("SKULL", "TARGET")):
            dmg = enemy.take_damage(28 + player.strength)
            return f"{title}: {dmg} KRITSCHADEN!"
        return None
    
    def _chicken_effect(self, player, enemy):
        """Das Huhn tut... irgendetwas"""
        player.chickens_summoned += 1
        roll = random.random()
        if roll < 0.20:
            dmg = random.randint(5, 20)
            actual = enemy.take_damage(dmg)
            return f"🐔 Das Huhn greift an! {actual} Schaden! Unerwartet."
        elif roll < 0.40:
            healed = player.heal_hp(random.randint(5, 15))
            return f"🐔 Das Huhn heilt dich! +{healed} HP. Warum auch nicht."
        elif roll < 0.55:
            gold = random.randint(8, 20)
            player.add_gold(gold)
            return f"🐔 Das Huhn legt Goldmünzen! +{gold} Gold."
        elif roll < 0.70:
            player.take_damage(random.randint(3, 8), ignore_block=True)
            return "🐔 Das Huhn pickt dich. Das tut weh. Schäm dich."
        elif roll < 0.82:
            dmg = 40
            actual = enemy.take_damage(dmg)
            return f"🐔 DAS HUHN IST EINE LEGENDE. {actual} SCHADEN. 🐔"
        elif roll < 0.92:
            enemy.weakened += 2
            return "🐔 Das Huhn starrt den Gegner an. Gegner geschwächt (2 Runden)."
        else:
            player.add_gold(5)
            player.heal_hp(5)
            enemy.take_damage(5)
            return "🐔 Das Huhn tut ALLES gleichzeitig. +5 Gold, +5 HP, 5 Schaden."
    
    def _chaos_effect(self, player, enemy, multiplier=1):
        """Komplette Zufallseffekte"""
        effects = []
        for _ in range(multiplier):
            roll = random.random()
            if roll < 0.15:
                effects.append("🎲 NICHTS PASSIERT. Das Universum zuckt mit den Schultern.")
            elif roll < 0.30:
                dmg = random.randint(5, 30) + player.strength
                actual = enemy.take_damage(dmg)
                effects.append(f"🎲 ZUFALLSSCHADEN: {actual}!")
            elif roll < 0.45:
                healed = player.heal_hp(random.randint(5, 25))
                effects.append(f"🎲 ZUFALLSHEILUNG: +{healed} HP!")
            elif roll < 0.58:
                gold = random.randint(5, 30)
                player.add_gold(gold)
                effects.append(f"🎲 ZUFALLSGOLD: +{gold}!")
            elif roll < 0.68:
                player.max_energy = min(6, player.max_energy + 1)
                effects.append("🎲 MAX ENERGIE +1! Für immer!")
            elif roll < 0.76:
                player.max_hp += random.randint(5, 15)
                effects.append("🎲 MAX HP erhöht!")
            elif roll < 0.83:
                dmg = random.randint(10, 20)
                player.take_damage(dmg, ignore_block=True)
                effects.append(f"🎲 SELBSTSCHADEN: -{dmg} HP. Tut leid.")
            elif roll < 0.89:
                player.strength += 2
                effects.append("🎲 +2 Stärke (diesen Kampf)!")
            elif roll < 0.94:
                enemy.burn += 3
                effects.append("🎲 GEGNER BRENNT! 3 Runden!")
            else:
                effects.append("🎲 DU HÖRST KURZ FERNE HÜHNER. Nichts passiert.")
        return effects
    
    def draw(self, screen, font_title, font_large, font_small, font_tiny):
        """Zeichnet den gesamten Spielautomaten"""
        if self.cabinet:
            cab = assets.scaled("ui", "slot_cabinet", self.cab_w, self.cab_h)
            # Glüh-Effekt nach Spin (rund ums Cabinet)
            if self.glow_timer > 0:
                ga = int(min(180, self.glow_timer * 100))
                glow = pygame.Surface((self.cab_w + 24, self.cab_h + 24), pygame.SRCALPHA)
                pygame.draw.rect(glow, (*GOLD, ga), (0, 0, self.cab_w + 24, self.cab_h + 24),
                                 border_radius=16)
                screen.blit(glow, (self.cab_x - 12, self.cab_y - 12))
            # Walzen zuerst, dann Cabinet als Rahmen darüber
            for reel in self.reels:
                reel.draw(screen, font_large, font_small)
            if cab:
                screen.blit(cab, (self.cab_x, self.cab_y))
            if self.spinning:
                spin_txt = font_small.render("⚡ SPINNING... ⚡", True, CYAN)
                screen.blit(spin_txt, (self.cab_x + self.cab_w // 2 - spin_txt.get_width() // 2,
                                       self.cab_y + self.cab_h + 2))
            if self.lucky_spin and (self.spinning or self.glow_timer > 0):
                lt = font_title.render("🍀 GLÜCKSDREH 🍀", True, (120, 235, 120))
                screen.blit(lt, (self.cab_x + self.cab_w // 2 - lt.get_width() // 2,
                                 self.cab_y - 22))
            return

        # ── Procedural-Fallback (kein Cabinet-Sprite) ──
        if self.glow_timer > 0:
            glow_alpha = int(min(180, self.glow_timer * 100))
            glow_surf = pygame.Surface((self.width + 20, self.height + 20), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (*GOLD, glow_alpha),
                             (0, 0, self.width + 20, self.height + 20), border_radius=12)
            screen.blit(glow_surf, (self.x - 10, self.y - 10))

        pygame.draw.rect(screen, SLOT_BG, (self.x, self.y, self.width, self.height), border_radius=10)
        pygame.draw.rect(screen, GOLD_DARK, (self.x, self.y, self.width, self.height), 3, border_radius=10)

        title = font_title.render("🎰 SLOT-O-MATIC 3000 🎰", True, GOLD)
        screen.blit(title, (self.x + self.width//2 - title.get_width()//2, self.y + 8))

        for reel in self.reels:
            reel.draw(screen, font_large, font_small)

        if self.spinning:
            spin_txt = font_small.render("⚡ SPINNING... ⚡", True, CYAN)
            screen.blit(spin_txt, (self.x + self.width//2 - spin_txt.get_width()//2,
                                   self.y + self.height - 22))
        if self.lucky_spin and (self.spinning or self.glow_timer > 0):
            lt = font_title.render("🍀 GLÜCKSDREH 🍀", True, (120, 235, 120))
            screen.blit(lt, (self.x + self.width // 2 - lt.get_width() // 2, self.y - 20))
