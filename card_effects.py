"""Karten-Effekte: Auflösung aller Karteneffekte"""

import random
from constants import *


class CardEffectResolver:
    """Löst Karteneffekte auf und gibt Beschreibungstexte zurück"""
    
    def resolve(self, card, player, enemy, slot_machine=None):
        """
        Löst einen Karteneffekt auf.
        Gibt Liste von Log-Strings zurück.
        """
        effect = card.effect
        logs = []
        
        if effect == "damage":
            dmg = card.damage + player.strength
            actual = enemy.take_damage(dmg)
            logs.append(f"⚔️ {card.name}: {actual} Schaden!")
        
        elif effect == "block":
            block_amount = card.block
            if player.shield_up:
                block_amount *= 2
            player.block += block_amount
            logs.append(f"🛡️ {card.name}: +{block_amount} Block!")
        
        elif effect == "heal":
            healed = player.heal_hp(card.heal)
            logs.append(f"💚 {card.name}: +{healed} HP geheilt!")
        
        elif effect == "lifesteal":
            dmg = card.damage + player.strength
            actual = enemy.take_damage(dmg)
            healed = player.heal_hp(card.heal)
            logs.append(f"🧛 {card.name}: {actual} Schaden, +{healed} HP gesaugt!")
        
        elif effect == "nuke":
            dmg = card.damage + player.strength * 2
            actual = enemy.take_damage(dmg)
            logs.append(f"☢️ NUCLEAR OPTION: {actual} MASSIVSCHADEN!")
            logs.append("   (Der Raum riecht jetzt nach verbranntem Plastik.)")
        
        elif effect == "coinflip":
            if random.random() < 0.5:
                dmg = 25 + player.strength
                actual = enemy.take_damage(dmg)
                logs.append(f"🪙 COIN FLIP: KOPF! {actual} Schaden! Glück gehabt!")
            else:
                self_dmg = random.randint(8, 15)
                player.take_damage(self_dmg, ignore_block=True)
                logs.append(f"🪙 COIN FLIP: ZAHL! {self_dmg} Selbstschaden. Pech gehabt.")
        
        elif effect == "tax_evasion":
            base_dmg = max(5, player.gold // 10) + card.damage + player.strength
            actual = enemy.take_damage(base_dmg)
            logs.append(f"📋 TAX EVASION: {actual} Schaden (Basis: dein Gold)!")
            logs.append("   'Das Finanzamt schaut weg.'")
        
        elif effect == "gambling":
            if player.spend_gold(10):
                dmg = random.randint(1, 40) + player.strength
                actual = enemy.take_damage(dmg)
                logs.append(f"🎰 GAMBLING ADDICTION: -10 Gold, {actual} Schaden!")
                if dmg > 30:
                    logs.append("   (Du riechst das Adrenalin. Du willst mehr.)")
                elif dmg < 10:
                    logs.append("   (Vielleicht nächstes Mal besser.)")
            else:
                logs.append("🎰 GAMBLING ADDICTION: Kein Gold! Die Karte lacht dich aus.")
        
        elif effect == "double_spin":
            if slot_machine:
                player.bonus_spins += 1
                logs.append("🎡 DOUBLE SPIN: +1 Bonus-Spin nach dem Hauptspin!")
                logs.append("   (Das Casino freut sich nicht darüber.)")
        
        elif effect == "triple_spin":
            if slot_machine:
                player.bonus_spins += 2
                logs.append("🎡🎡🎡 JACKPOT KARTE: +2 Bonus-Spins!")
                logs.append("   (Der Automat seufzt leise.)")
        
        elif effect == "greed":
            player.add_gold(15)
            old_max = player.max_hp
            player.max_hp = max(20, player.max_hp - 5)
            player.hp = min(player.hp, player.max_hp)
            logs.append(f"💰 GREED: +15 Gold! Max HP -{old_max - player.max_hp}.")
            logs.append("   'Geld ist alles. HP ist Schwäche.'")
        
        elif effect == "chicken":
            player.chickens_summoned += 1
            roll = random.random()
            if roll < 0.25:
                dmg = random.randint(10, 25) + player.strength
                actual = enemy.take_damage(dmg)
                logs.append(f"🐔 SUMMON CHICKEN: Das Huhn greift an! {actual} Schaden!")
            elif roll < 0.45:
                healed = player.heal_hp(random.randint(8, 18))
                logs.append(f"🐔 SUMMON CHICKEN: Das Huhn heilt! +{healed} HP!")
            elif roll < 0.60:
                gold = random.randint(10, 22)
                player.add_gold(gold)
                logs.append(f"🐔 SUMMON CHICKEN: Das Huhn bringt Gold! +{gold}!")
            elif roll < 0.72:
                player.strength += 2
                logs.append("🐔 SUMMON CHICKEN: Das Huhn gibt Stärke! +2 STR!")
            elif roll < 0.82:
                logs.append("🐔 SUMMON CHICKEN: Das Huhn schaut dich an. Geht wieder.")
                logs.append("   (Du bist tief bewegt.)")
            else:
                # Ultra-rare
                dmg = 50 + player.strength
                actual = enemy.take_damage(dmg)
                player.heal_hp(20)
                player.add_gold(15)
                logs.append(f"🐔👑 DAS HUHN IST DER HÜHNER-KÖNIG! {actual} Schaden, +20 HP, +15 Gold!")
        
        elif effect == "chaos":
            logs.append("🌀 POTION OF CHAOS: Du trinkst es. Hier kommt...")
            chaos_roll = random.random()
            if chaos_roll < 0.12:
                player.max_hp += 20
                player.hp += 20
                logs.append("   ...MAX HP +20! Glückskind!")
            elif chaos_roll < 0.24:
                player.max_energy += 1
                logs.append("   ...MAX ENERGIE +1! Für immer!")
            elif chaos_roll < 0.36:
                dmg = random.randint(20, 50) + player.strength
                actual = enemy.take_damage(dmg)
                logs.append(f"   ...{actual} CHAOS-SCHADEN!")
            elif chaos_roll < 0.48:
                player.strength += random.randint(2, 5)
                logs.append(f"   ...MASSIVER STÄRKE-BOOST!")
            elif chaos_roll < 0.60:
                healed = player.heal_hp(player.max_hp // 2)
                logs.append(f"   ...HALBHEILUNG: +{healed} HP!")
            elif chaos_roll < 0.70:
                self_dmg = random.randint(10, 25)
                player.take_damage(self_dmg, ignore_block=True)
                logs.append(f"   ...SELBSTSCHADEN: -{self_dmg} HP. Oops.")
            elif chaos_roll < 0.80:
                player.add_gold(random.randint(20, 50))
                logs.append("   ...GOLDREGEN! Viel Gold!")
            elif chaos_roll < 0.88:
                logs.append("   ...NICHTS. Das Universum ist grausam.")
            elif chaos_roll < 0.94:
                # Beschwört eine zufällige Karte aus dem Pool
                import random as rnd
                from constants import CARD_DEFINITIONS
                new_card_def = rnd.choice(CARD_DEFINITIONS)
                player.add_card_to_deck(new_card_def)
                logs.append(f"   ...Neue Karte im Deck: '{new_card_def['name']}'!")
            else:
                logs.append("   ...DU SIEHST KURZ DIE WAHRHEIT DES UNIVERSUMS.")
                logs.append("   Sie ist ein Huhn. Du bist beruhigt.")
                player.chickens_summoned += 1
        
        elif effect == "execrate":
            base_dmg = enemy.max_hp // 3 + player.strength
            actual = enemy.take_damage(base_dmg)
            logs.append(f"☠️ DAS ENDE: {actual} Schaden (1/3 des Gegner-Max-HP)!")
            logs.append("   'Es tut mir leid. Nein, tut es nicht.'")
        
        # ═══ NEUE EFFEKTE ═══
        elif effect == "double_strike":
            total = 0
            for _ in range(2):
                total += enemy.take_damage(card.damage + player.strength)
            logs.append(f"⚔️⚔️ DOPPELHIEB: 2 Treffer, {total} Schaden gesamt!")
        
        elif effect == "lucky_hit":
            if random.random() < 0.3:
                dmg = (card.damage + player.strength) * 3
                actual = enemy.take_damage(dmg)
                logs.append(f"🍀 GLÜCKSTREFFER: KRITISCH! {actual} Schaden (x3)!")
            else:
                actual = enemy.take_damage(card.damage + player.strength)
                logs.append(f"🍀 Glückstreffer: {actual} Schaden (kein Krit).")
        
        elif effect == "rage":
            missing = player.max_hp - player.hp
            dmg = missing * 2 + player.strength
            actual = enemy.take_damage(dmg)
            logs.append(f"😡 WUTAUSBRUCH: {actual} Schaden (2x fehlende HP)!")
            if missing == 0:
                logs.append("   (Du bist bei voller HP. Wenig Wut. Wenig Schaden.)")
        
        elif effect == "bribe":
            if player.spend_gold(20):
                dmg = 30 + player.strength
                actual = enemy.take_damage(dmg)
                logs.append(f"💵 BESTECHUNG: -20 Gold, {actual} Schaden gekauft!")
            else:
                logs.append("💵 BESTECHUNG: Zu arm zum Bestechen. Peinlich.")
        
        elif effect == "all_in":
            bet = player.gold
            if bet > 0:
                player.gold = 0
                dmg = bet + player.strength
                actual = enemy.take_damage(dmg)
                logs.append(f"🎰 ALL IN: {bet} Gold gesetzt, {actual} Schaden!")
                logs.append("   (Du bist jetzt pleite. War es das wert?)")
            else:
                logs.append("🎰 ALL IN: Du hast kein Gold. All Out.")
        
        elif effect == "second_wind":
            missing = player.max_hp - player.hp
            healed = player.heal_hp(missing // 4)
            logs.append(f"😮‍💨 ZWEITE LUFT: +{healed} HP geheilt!")
        
        elif effect == "reflect":
            player.block += card.block
            player.reflect = True
            logs.append(f"🪞 REFLEKTOR: +{card.block} Block, nächster Schaden wird reflektiert!")
        
        elif effect == "adrenaline":
            player.energy += 2
            if player.deck or player.discard:
                player.draw_hand(1)
            logs.append("💉 ADRENALIN: +2 Energie, +1 Karte gezogen!")
        
        elif effect == "train":
            player.strength += 2
            logs.append("🏋️ KRAFTTRAINING: +2 Stärke dauerhaft!")
        
        elif effect == "loaded_dice":
            player.lucky += 2
            logs.append("🎲 MANIPULIERTER WÜRFEL: +2 Glücksrunden!")
            logs.append("   (Das Casino bemerkt nichts. Vorerst.)")
        
        elif effect == "coin_rain":
            player.coin_rain_active = True
            logs.append("🪙 MÜNZREGEN AKTIV: +10 Gold je gespielter Karte diese Runde!")
        
        elif effect == "chicken_swarm":
            logs.append("🐔🐔🐔 HÜHNERSCHWARM: Drei Hühner stürmen los!")
            for n in range(3):
                logs.append("   " + self._quick_chicken(player, enemy))
        
        elif effect == "roulette":
            if random.random() < (1/6):
                player.take_damage(40, ignore_block=True)
                logs.append("🔫 RUSSISCH ROULETTE: KLICK-BANG! -40 HP! Autsch.")
            else:
                actual = enemy.take_damage(40 + player.strength)
                logs.append(f"🔫 RUSSISCH ROULETTE: Leer! {actual} Schaden am Gegner!")
        
        elif effect == "redraw":
            n = len(player.hand)
            player.discard.extend(player.hand)
            player.hand = []
            player.draw_hand(n)
            logs.append(f"🔄 NEUSTART: {n} Karten neu gezogen!")

        elif effect == "plague_breath":
            dmg = card.damage + player.strength
            actual = enemy.take_damage(dmg)
            enemy.burn += 2
            logs.append(f"🤢 PESTHAUCH: {actual} Schaden, Gegner brennt 2 Runden!")

        elif effect == "shield_wall":
            block_amount = 3 * len(player.hand)
            player.block += block_amount
            logs.append(f"🧱 SCHILDWALL: +{block_amount} Block ({len(player.hand)} Karten × 3)!")

        elif effect == "berserker":
            dmg = card.damage + player.strength
            actual = enemy.take_damage(dmg)
            player.max_hp = max(10, player.max_hp - 3)
            player.hp = min(player.hp, player.max_hp)
            logs.append(f"😤 BERSERKER: {actual} Schaden! Aber -3 Max HP dauerhaft.")

        elif effect == "pillage":
            dmg = card.damage + player.strength
            actual = enemy.take_damage(dmg)
            loot = enemy.armor
            if loot > 0:
                player.add_gold(loot)
                logs.append(f"💰 RAUBZUG: {actual} Schaden, +{loot} Gold geplündert!")
            else:
                logs.append(f"💰 RAUBZUG: {actual} Schaden (keine Rüstung zu plündern).")

        elif effect == "iron_storm":
            dmg = max(0, player.block) + player.strength
            actual = enemy.take_damage(dmg)
            logs.append(f"🌪️ EISENSTURM: {actual} Schaden (= {player.block} Block als Waffe)!")

        elif effect == "shadow_step":
            player.energy += 1
            player.next_free_card = True
            logs.append("👻 SCHATTENSCHRITT: +1 Energie! Nächste Karte kostet 0.")

        elif effect == "retribution":
            total_taken = getattr(player, '_total_damage_taken', 0)
            dmg = max(5, total_taken // 10) + player.strength
            actual = enemy.take_damage(dmg)
            logs.append(f"⚖️ VERGELTUNG: {actual} Schaden (basiert auf erhaltenem Schaden)!")

        # ═══ EXHAUST-KARTEN ═══
        elif effect == "annihilate":
            dmg = card.damage + player.strength
            actual = enemy.take_damage(dmg)
            logs.append(f"💥 VERNICHTUNG: {actual} Schaden! Die Karte zerfällt zu Staub.")

        elif effect == "last_resort":
            healed = player.heal_hp(player.max_hp)
            player.strength += 3
            logs.append(f"🃏 LETZTER TRUMPF: +{healed} HP, +3 Stärke! Karte verbraucht.")

        elif effect == "gold_rush":
            player.add_gold(60)
            logs.append("💸 GOLDRAUSCH: +60 Gold! Die Karte löst sich auf.")

        # ═══ FLUCH-KARTEN ═══
        elif effect == "curse_nausea":
            player.take_damage(6, ignore_block=True)
            logs.append("🤮 FLUCH ÜBELKEIT: -6 HP. Warum hast du das gespielt?")

        elif effect == "curse_unluck":
            lost = min(10, player.gold)
            player.gold -= lost
            logs.append(f"🌑 FLUCH PECH: -{lost} Gold. Einfach weg.")

        elif effect == "curse_burden":
            player.energy = max(0, player.energy - 1)
            logs.append("⛓️ FLUCH LAST: -1 Energie. Schwer wie Blei.")

        # ═══ Neue Effekte v1.8.0: Gift, Debuff, Risiko ═══
        elif effect == "poison_blade":
            dmg = card.damage + player.strength
            actual = enemy.take_damage(dmg)
            stacks = 3 + (1 if player.has_relic("poison_boost") else 0)
            enemy.poison += stacks
            logs.append(f"🐍 {card.name}: {actual} Schaden + {stacks} Gift!")

        elif effect == "toxic_cloud":
            stacks = 5 + (1 if player.has_relic("poison_boost") else 0)
            enemy.poison += stacks
            logs.append(f"☠️ {card.name}: +{stacks} Gift! Der Gegner hat jetzt {enemy.poison} Gift.")

        elif effect == "acid_barrel":
            dmg = card.damage + player.strength
            actual = enemy.take_damage(dmg)
            if enemy.poison > 0:
                bonus = 1 if player.has_relic("poison_boost") else 0
                enemy.poison = enemy.poison * 2 + bonus
                logs.append(f"🧪 {card.name}: {actual} Schaden, Gift VERDOPPELT auf {enemy.poison}!")
            else:
                logs.append(f"🧪 {card.name}: {actual} Schaden. (Kein Gift zum Verdoppeln ...)")

        elif effect == "expose":
            dmg = card.damage + player.strength
            actual = enemy.take_damage(dmg)
            rounds = 2 + (1 if player.has_relic("anatomy") else 0)
            enemy.vulnerable += rounds
            logs.append(f"🎯 {card.name}: {actual} Schaden + {rounds} Runden Verwundbar!")

        elif effect == "executioner":
            dmg = card.damage + player.strength
            if enemy.poison > 0:
                dmg = int(dmg * 1.5)
            actual = enemy.take_damage(dmg)
            note = " (Gift-Bonus!)" if enemy.poison > 0 else ""
            logs.append(f"🪓 {card.name}: {actual} Schaden{note}")

        elif effect == "regen_potion":
            player.regen += 4
            logs.append(f"🌿 {card.name}: +4 Regeneration (heilt 4, 3, 2, 1 HP)!")

        elif effect == "spike_skin":
            block_amount = card.block
            if player.shield_up:
                block_amount *= 2
            player.block += block_amount
            player.thorns += 4
            logs.append(f"🌵 {card.name}: +{block_amount} Block, +4 Dornen (ganzer Kampf)!")

        elif effect == "blood_pact":
            player.take_damage(5, ignore_block=True)
            player.energy += 2
            logs.append(f"🩸 {card.name}: −5 HP, +2 Energie. Der Pakt ist besiegelt.")

        # ═══ Klassen-Karten v1.9.0 ═══
        elif effect == "warcry":
            player.strength += 2
            player.block += 6
            logs.append(f"📢 {card.name}: +2 Stärke, +6 Block!")

        elif effect == "shield_bash":
            dmg = player.block + player.strength
            actual = enemy.take_damage(dmg)
            logs.append(f"🛡️ {card.name}: {actual} Schaden (= Block)!")

        elif effect == "bloodletting":
            dmg = card.damage + player.strength
            actual = enemy.take_damage(dmg)
            stacks = 2 + (1 if player.has_relic("poison_boost") else 0)
            enemy.poison += stacks
            healed = player.heal_hp(3)
            logs.append(f"🩸 {card.name}: {actual} Schaden, +{stacks} Gift, +{healed} HP!")

        elif effect == "lucky_streak":
            player.lucky += 2
            drawn = player.draw_hand(1)
            logs.append(f"🍀 {card.name}: +2 Glücksrunden, +{drawn} Karte!")

        elif effect == "brew_poison":
            stacks = 7 + (1 if player.has_relic("poison_boost") else 0)
            enemy.poison += stacks
            logs.append(f"🧪 {card.name}: +{stacks} Gift! ({enemy.poison} total)")

        elif effect == "card_trick":
            drawn = player.draw_hand(2)
            logs.append(f"🃏 {card.name}: +{drawn} Karten gezogen!")

        else:
            logs.append(f"❓ {card.name}: Unbekannter Effekt '{effect}'. Seltsam.")

        return logs
    
    def _quick_chicken(self, player, enemy):
        """Kurzer Hühner-Effekt für den Schwarm"""
        player.chickens_summoned += 1
        roll = random.random()
        if roll < 0.3:
            actual = enemy.take_damage(random.randint(5, 18))
            return f"🐔 Huhn greift an: {actual} Schaden!"
        elif roll < 0.5:
            healed = player.heal_hp(random.randint(5, 12))
            return f"🐔 Huhn heilt: +{healed} HP!"
        elif roll < 0.7:
            g = random.randint(5, 15)
            player.add_gold(g)
            return f"🐔 Huhn bringt Gold: +{g}!"
        elif roll < 0.85:
            enemy.weakened += 1
            return "🐔 Huhn schwächt den Gegner!"
        else:
            return "🐔 Huhn rennt im Kreis. Nutzlos."
