"""Haupt-Spielklasse: State Machine für alle Spielphasen"""

import pygame
import random
import time
import math
from constants import *
from entities import Player, Enemy, Card
from slots import SlotMachine
from ui import UIRenderer
from card_effects import CardEffectResolver
from highscores import load_highscores, add_highscore, calculate_score
import savegame
import audio
import mapgen
import options


# ═══════════════════════════════════════════════
# SPIELPHASEN
# ═══════════════════════════════════════════════
STATE_MENU        = "menu"
STATE_TUTORIAL    = "tutorial"       # Tutorial-Bildschirm
STATE_CHANGELOG   = "changelog"      # "Was ist neu" Kurz-Changelist
STATE_OPTIONS     = "options"        # Optionen-/Einstellungsmenü
STATE_PAUSE       = "pause"          # Pause-/Speichern-Menü
STATE_MAP         = "map"            # Pfad-/Etagenkarte
STATE_REST        = "rest"           # Lagerfeuer
STATE_COMBAT      = "combat"
STATE_PLAYER_TURN = "player_turn"    # Karten spielen
STATE_SLOT_SPIN   = "slot_spin"      # Slot dreht sich
STATE_ENEMY_TURN  = "enemy_turn"     # Gegner agiert
STATE_REWARD      = "reward"         # Belohnungsbildschirm
STATE_EVENT       = "event"          # Zufalls-Event zwischen Etagen
STATE_SHOP        = "shop"           # Laden zwischen Etagen
STATE_GAME_OVER   = "game_over"
STATE_VICTORY     = "victory"
STATE_SCORES      = "scores"         # Highscore-Anzeige


class Game:
    """Zentrale Spielklasse: Verwaltet alle Zustände und den Spielfluss"""
    
    def __init__(self, screen, clock):
        # 'screen' ist das echte Fenster; gezeichnet wird auf eine Canvas,
        # die am Frame-Ende mit Screen-Shake-Versatz aufs Fenster geblittet wird.
        self.display = screen
        self.screen = pygame.Surface((SCREEN_W, SCREEN_H))
        self.clock = clock
        self.ui = UIRenderer(self.screen)
        self.resolver = CardEffectResolver()

        # Juice
        self.shake = 0.0
        self.hitstop = 0.0
        self.particles = []   # [x, y, vx, vy, life, maxlife, color, size]
        
        self.state = STATE_MENU
        self.running = True
        
        # Spielzustand
        self.player = None
        self.enemy = None
        self.floor_num = 1
        self.turn_num = 1
        self.combat_log = []
        
        # Slot-Maschine (position rechts oben im Kampf)
        self.slot_machine = None
        
        # UI-Zustände
        self.selected_card = None
        self.hovered_card_idx = None
        self.card_rects = []
        self.reward_cards = []
        self.gold_reward = 0
        self.reward_card_rects = []
        self.reward_skip_rect = None
        self.reward_relic = None      # Relikt-Belohnung (Elite/Boss)

        # Combo-System
        self.combo_type = None
        self.combo_count = 0
        self.combo_flash = 0.0        # Anzeige-Puls

        # Event-Zustand
        self.current_event = None
        self.event_option_rects = []
        self.event_resolved = False
        self.event_result = ""
        self.event_continue_rect = None
        self.hovered_event_idx = None
        
        # Phase innerhalb Kampf
        self.sub_phase = "cards"     # "cards" | "slot" | "enemy"
        self.slot_done = False
        self.cards_played_this_turn = 0
        self.enemy_turn_timer = 0.0
        self.enemy_turn_log = []
        
        # Animations-Queue für Schadenszahlen
        self.damage_numbers = []  # [(text, x, y, color, timer)]

        # Slot-Effekte anzeigen Timer
        self.slot_effect_display_timer = 0.0
        self.slot_effects_shown = []

        # Slot-Tod-Verzögerung (TODO #6)
        self.slot_death_pending = False
        self.slot_death_timer = 0.0

        # Kampflog-Scroll (TODO #10)
        self.log_scroll = 0

        # Bonus-Spins-Counter
        self.spins_remaining = 1
        
        # Shop-Zustand
        self.shop_items = []          # aktuell angebotene Items
        self.shop_item_rects = []
        self.shop_leave_rect = None
        self.shop_message = ""
        self.shop_message_timer = 0.0
        self.shop_gamble_rect = None
        self.shop_remove_mode = False  # Karte-entfernen-Auswahl aktiv
        self.shop_remove_rects = []
        self.shop_upgrade_mode = False # Karte-aufwerten-Auswahl aktiv
        self.shop_upgrade_rects = []
        self.shop_pending_cost = 0
        self.shop_purchased = set()    # bereits gekaufte Items im aktuellen Shop
        
        # Highscore-Zustand
        self.highscores = load_highscores()
        self.last_score = 0
        self.last_rank = None
        self.last_is_record = False
        self.score_saved = False
        
        # Highscore-Anzeige Rückkehr-Button
        self.scores_back_rect = None

        # Pause / Speichern
        self._prev_state = STATE_PLAYER_TURN  # Zustand vor dem Pausieren
        self.menu_buttons = {}                # Layout-Rects fürs Hauptmenü

        # Pfad-/Map-System
        self.act = 1
        self.gamemap = None
        self.map_current = None     # [row, col] des zuletzt besuchten Knotens
        self.current_node = None    # Knoten, der gerade gespielt wird
        self.hovered_node = None    # [row, col] für Hover-Highlight
        self.map_message = ""
        self.map_message_timer = 0.0
        self.upgrade_ctx = None     # "shop" | "rest" – Kontext der Schmiede

        # Optionen
        self.options = options.load()
        self.options_drag = None          # (key, track_rect) während Slider-Ziehen
        self._options_return = STATE_MENU  # wohin "Zurück" im Options-Menü führt
        self._apply_options()
        self._apply_fullscreen()

        # "Was ist neu?": einmalig nach einem Update anzeigen
        if self.options.get("last_seen") != GAME_VERSION:
            self.state = STATE_CHANGELOG
            self.options["last_seen"] = GAME_VERSION
            options.save(self.options)

    # ═══════════════════════════════════════════════
    # OPTIONEN ANWENDEN
    # ═══════════════════════════════════════════════

    def _apply_options(self):
        audio.set_master(self.options["master"])
        audio.set_music(self.options["music"])
        audio.set_sfx(self.options["sfx"])

    def _apply_fullscreen(self):
        flags = (pygame.SCALED | pygame.FULLSCREEN) if self.options.get("fullscreen") else 0
        try:
            self.display = pygame.display.set_mode((SCREEN_W, SCREEN_H), flags)
        except Exception:
            self.options["fullscreen"] = False
            try:
                self.display = pygame.display.set_mode((SCREEN_W, SCREEN_H))
            except Exception:
                pass

    # ═══════════════════════════════════════════════
    # MAIN LOOP
    # ═══════════════════════════════════════════════
    
    def run(self):
        dt = 0.0
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            self.ui.tick(dt)

            self._handle_events()
            self._update(dt)
            self._draw()

            # Canvas mit Screen-Shake-Versatz aufs Fenster bringen
            ox = oy = 0
            if self.shake > 0.5:
                ox = int(random.uniform(-self.shake, self.shake))
                oy = int(random.uniform(-self.shake, self.shake))
            self.display.fill(DARKER_BG)
            self.display.blit(self.screen, (ox, oy))
            pygame.display.flip()
    
    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self._handle_escape()
                elif event.key == pygame.K_r:
                    if self.state in (STATE_GAME_OVER, STATE_VICTORY):
                        self._start_game()
                elif event.key == pygame.K_m:
                    audio.toggle_mute()

            if event.type == pygame.MOUSEWHEEL:
                self._handle_scroll(event.y)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._handle_click(pygame.mouse.get_pos())

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if self.options_drag:
                    self.options_drag = None
                    options.save(self.options)

            if event.type == pygame.MOUSEMOTION:
                self._handle_hover(pygame.mouse.get_pos())
    
    # Zustände, in denen ein laufender Run pausiert/gespeichert werden kann
    RUN_STATES = (STATE_PLAYER_TURN, STATE_SLOT_SPIN, STATE_ENEMY_TURN,
                  STATE_SHOP, STATE_EVENT, STATE_REWARD, STATE_MAP, STATE_REST)

    def _handle_escape(self):
        """ESC: kontextabhängig pausieren, zurück oder beenden"""
        if self.state == STATE_OPTIONS:
            options.save(self.options)
            self.state = self._options_return
        elif self.state in self.RUN_STATES:
            self._prev_state = self.state
            self.state = STATE_PAUSE
        elif self.state == STATE_PAUSE:
            self.state = self._prev_state           # Weiter spielen
        elif self.state in (STATE_TUTORIAL, STATE_SCORES, STATE_CHANGELOG,
                            STATE_GAME_OVER, STATE_VICTORY):
            self.state = STATE_MENU
        else:  # Hauptmenü
            self.running = False

    def _compute_menu_layout(self):
        """Layout der Hauptmenü-Buttons. Quelle für Zeichnen UND Klick."""
        cx = SCREEN_W // 2
        changelog = pygame.Rect(16, SCREEN_H - 50, 200, 34)
        if savegame.has_valid_save():
            return {
                "resume":   pygame.Rect(cx - 130, 430, 260, 54),
                "play":     pygame.Rect(cx - 130, 490, 260, 44),
                "tutorial": pygame.Rect(cx - 110, 540, 220, 40),
                "options":  pygame.Rect(cx - 110, 586, 220, 40),
                "scores":   pygame.Rect(cx - 110, 632, 220, 40),
                "changelog": changelog,
            }
        return {
            "resume":   None,
            "play":     pygame.Rect(cx - 110, 458, 220, 54),
            "tutorial": pygame.Rect(cx - 110, 520, 220, 42),
            "options":  pygame.Rect(cx - 110, 570, 220, 42),
            "scores":   pygame.Rect(cx - 110, 620, 220, 42),
            "changelog": changelog,
        }

    def _compute_pause_layout(self):
        """Layout der Pause-Menü-Buttons"""
        cx = SCREEN_W // 2
        return {
            "resume":    pygame.Rect(cx - 160, 296, 320, 50),
            "options":   pygame.Rect(cx - 160, 352, 320, 44),
            "save_quit": pygame.Rect(cx - 160, 402, 320, 50),
            "menu":      pygame.Rect(cx - 160, 458, 320, 44),
        }

    def _compute_options_layout(self):
        """Layout des Optionsmenüs (Slider + Toggles)."""
        cx = SCREEN_W // 2
        px = cx - 300
        sliders = {
            "master": pygame.Rect(px + 250, 236, 250, 10),
            "music":  pygame.Rect(px + 250, 292, 250, 10),
            "sfx":    pygame.Rect(px + 250, 348, 250, 10),
        }
        toggles = {
            "fullscreen": pygame.Rect(px + 488, 406, 72, 32),
            "shake":      pygame.Rect(px + 488, 454, 72, 32),
            "particles":  pygame.Rect(px + 488, 502, 72, 32),
        }
        return {
            "panel": pygame.Rect(px, 150, 600, 470),
            "sliders": sliders,
            "toggles": toggles,
            "back":     pygame.Rect(cx - 200, 558, 180, 44),
            "defaults": pygame.Rect(cx + 20, 558, 180, 44),
        }

    def _set_slider(self, key, mx, track):
        val = max(0.0, min(1.0, (mx - track.x) / track.w))
        self.options[key] = round(val, 2)
        self._apply_options()

    def _handle_options_click(self, pos):
        lay = self._compute_options_layout()
        for key, tr in lay["sliders"].items():
            if tr.inflate(24, 28).collidepoint(pos):
                self._set_slider(key, pos[0], tr)
                self.options_drag = (key, tr)
                return
        for key, tr in lay["toggles"].items():
            if tr.collidepoint(pos):
                self.options[key] = not self.options[key]
                audio.click()
                if key == "fullscreen":
                    self._apply_fullscreen()
                options.save(self.options)
                return
        if lay["back"].collidepoint(pos):
            audio.click(); options.save(self.options); self.state = self._options_return
            return
        if lay["defaults"].collidepoint(pos):
            audio.click()
            self.options = dict(options.DEFAULTS)
            self._apply_options(); self._apply_fullscreen(); options.save(self.options)
            return

    def _handle_hover(self, pos):
        # Slider ziehen
        if self.state == STATE_OPTIONS and self.options_drag and pygame.mouse.get_pressed()[0]:
            key, tr = self.options_drag
            self._set_slider(key, pos[0], tr)
            return
        if self.state == STATE_PLAYER_TURN and self.card_rects:
            self.hovered_card_idx = None
            for i, rect in enumerate(self.card_rects):
                if rect and rect.collidepoint(pos):
                    self.hovered_card_idx = i
                    break
        elif self.state == STATE_EVENT and not self.event_resolved:
            self.hovered_event_idx = None
            for i, rect in enumerate(self.event_option_rects):
                if rect and rect.collidepoint(pos):
                    self.hovered_event_idx = i
                    break
        elif self.state == STATE_MAP:
            self.hovered_node = None
            for n in self._map_available():
                if (pos[0] - n["x"]) ** 2 + (pos[1] - n["y"]) ** 2 <= (mapgen.NODE_R + 6) ** 2:
                    self.hovered_node = [n["row"], n["col"]]
                    break

    def _handle_scroll(self, delta_y):
        """Mausrad-Scrolling für das Kampflog"""
        log_rect = pygame.Rect(420, 290, 380, 195)
        if log_rect.collidepoint(pygame.mouse.get_pos()):
            max_scroll = max(0, len(self.combat_log) - 5)
            self.log_scroll = max(0, min(max_scroll, self.log_scroll + delta_y))
    
    def _handle_click(self, pos):
        mx, my = pos

        # Globale Overlays (Schmiede/Verbrennen) – über jedem State
        if self.shop_upgrade_mode:
            self._handle_upgrade_click(pos)
            return
        if self.shop_remove_mode:
            self._handle_remove_click(pos)
            return

        if self.state == STATE_MAP:
            self._handle_map_click(pos)
            return

        if self.state == STATE_REST:
            self._handle_rest_click(pos)
            return

        if self.state == STATE_MENU:
            lay = self._compute_menu_layout()
            if lay["resume"] and lay["resume"].collidepoint(pos):
                audio.play("click"); self._load_run()
                return
            if lay["play"].collidepoint(pos):
                audio.play("click"); self._start_game()
                return
            if lay["tutorial"].collidepoint(pos):
                audio.play("click"); self.state = STATE_TUTORIAL
                return
            if lay["options"].collidepoint(pos):
                audio.play("click"); self._options_return = STATE_MENU; self.state = STATE_OPTIONS
                return
            if lay["scores"].collidepoint(pos):
                audio.play("click"); self.state = STATE_SCORES
                return
            if lay["changelog"].collidepoint(pos):
                audio.play("click"); self.state = STATE_CHANGELOG
                return

        elif self.state == STATE_CHANGELOG:
            back = pygame.Rect(SCREEN_W//2 - 100, SCREEN_H - 62, 200, 44)
            if back.collidepoint(pos):
                audio.play("click"); self.state = STATE_MENU
            return

        elif self.state == STATE_PAUSE:
            lay = self._compute_pause_layout()
            if lay["resume"].collidepoint(pos):
                audio.play("click"); self.state = self._prev_state
            elif lay["options"].collidepoint(pos):
                audio.play("click"); self._options_return = STATE_PAUSE; self.state = STATE_OPTIONS
            elif lay["save_quit"].collidepoint(pos):
                self._save_and_quit()
            elif lay["menu"].collidepoint(pos):
                # Hauptmenü ohne Speichern (Run wird verworfen)
                audio.play("click"); self.state = STATE_MENU
            return

        elif self.state == STATE_OPTIONS:
            self._handle_options_click(pos)
            return

        elif self.state == STATE_TUTORIAL:
            back_btn = pygame.Rect(SCREEN_W//2 - 100, SCREEN_H - 62, 200, 44)
            if back_btn.collidepoint(pos):
                self.state = STATE_MENU

        elif self.state == STATE_PLAYER_TURN:
            # Karte klicken (Crash-Fix: card_rects kann [] sein)
            for i, (rect, card) in enumerate(zip(self.card_rects or [], self.player.hand or [])):
                if rect and rect.collidepoint(pos):
                    self._try_play_card(card)
                    return
            
            # "Runde beenden" Button
            end_btn = pygame.Rect(SCREEN_W - 170, SCREEN_H//2 - 25, 160, 50)
            if end_btn.collidepoint(pos):
                self._start_slot_phase()
                return
            
            # Karte abwählen
            self.selected_card = None
        
        elif self.state == STATE_SLOT_SPIN:
            # Spin-Button
            if self.spins_remaining > 0 and not self.slot_machine.spinning:
                spin_btn = pygame.Rect(SCREEN_W//2 - 80, 680, 160, 45)
                if spin_btn.collidepoint(pos):
                    self._do_spin()
            
            # Weiter-Button: sobald keine Spins mehr offen sind (auch bei 0 Spins
            # durch Slot-Jam) und gerade nichts dreht -> Softlock-Fix
            if (self.spins_remaining == 0 and not self.slot_machine.spinning
                    and not self.slot_death_pending):
                next_btn = pygame.Rect(SCREEN_W//2 - 80, 735, 160, 40)
                if next_btn.collidepoint(pos):
                    self._start_enemy_turn()
        
        elif self.state == STATE_REWARD:
            if self.reward_card_rects:
                for i, rect in enumerate(self.reward_card_rects):
                    if rect.collidepoint(pos):
                        self._pick_reward_card(i)
                        return
            if self.reward_skip_rect and self.reward_skip_rect.collidepoint(pos):
                self._skip_reward()
        
        elif self.state == STATE_EVENT:
            self._handle_event_click(pos)

        elif self.state == STATE_SHOP:
            self._handle_shop_click(pos)

        elif self.state == STATE_SCORES:
            if self.scores_back_rect and self.scores_back_rect.collidepoint(pos):
                self.state = STATE_MENU
        
        elif self.state == STATE_GAME_OVER:
            # Klick auf "Bestenliste"
            sc_btn = pygame.Rect(SCREEN_W//2 - 100, SCREEN_H - 120, 200, 45)
            if sc_btn.collidepoint(pos):
                self.state = STATE_SCORES

    def _handle_remove_click(self, pos):
        """Klicks im Karte-Verbrennen-Overlay"""
        cancel = pygame.Rect(SCREEN_W//2 - 80, SCREEN_H - 70, 160, 40)
        for rect, card in self.shop_remove_rects:
            if rect.collidepoint(pos):
                self._remove_card_from_deck(card)
                return
        if cancel.collidepoint(pos):
            self.shop_remove_mode = False

    def _handle_upgrade_click(self, pos):
        """Klicks im Schmiede-Overlay (Shop oder Lagerfeuer)"""
        cancel = pygame.Rect(SCREEN_W//2 - 80, SCREEN_H - 70, 160, 40)
        for rect, card in self.shop_upgrade_rects:
            if rect.collidepoint(pos):
                self._upgrade_card_in_deck(card)
                return
        if cancel.collidepoint(pos):
            self.shop_upgrade_mode = False  # zurück zum darunterliegenden Screen

    def _handle_shop_click(self, pos):
        """Verarbeitet Klicks im Shop"""
        # Normale Shop-Items
        for rect, item in self.shop_item_rects:
            if rect.collidepoint(pos):
                self._buy_shop_item(item)
                return
        
        # Gambling-Automat
        if self.shop_gamble_rect and self.shop_gamble_rect.collidepoint(pos):
            self._gamble()
            return
        
        # Verlassen
        if self.shop_leave_rect and self.shop_leave_rect.collidepoint(pos):
            self._leave_shop()

    def _handle_map_click(self, pos):
        """Klick auf einen erreichbaren Karten-Knoten"""
        mx, my = pos
        for n in self._map_available():
            if (mx - n["x"]) ** 2 + (my - n["y"]) ** 2 <= (mapgen.NODE_R + 6) ** 2:
                self._enter_node(n)
                return

    def _compute_rest_layout(self):
        cx = SCREEN_W // 2
        return {
            "heal":    pygame.Rect(cx - 320, 360, 300, 120),
            "upgrade": pygame.Rect(cx + 20, 360, 300, 120),
            "leave":   pygame.Rect(cx - 90, 540, 180, 46),
        }

    def _handle_rest_click(self, pos):
        """Klicks am Lagerfeuer"""
        lay = self._compute_rest_layout()
        if lay["heal"].collidepoint(pos):
            healed = self.player.heal_hp(int(self.player.max_hp * 0.30))
            self._fx_heal(healed)
            self.map_message = f"🔥 Ausgeruht: +{healed} HP"
            self.map_message_timer = 2.5
            self._finish_node()
        elif lay["upgrade"].collidepoint(pos):
            upgradeable = [c for c in self.player.deck + self.player.discard + self.player.hand
                           if c.can_upgrade()]
            if not upgradeable:
                audio.play("error", 0.6)
                return
            self.upgrade_ctx = "rest"
            self.shop_upgrade_mode = True
        elif lay["leave"].collidepoint(pos):
            audio.play("click")
            self._finish_node()

    def _handle_event_click(self, pos):
        """Verarbeitet Klicks im Event-Screen"""
        if not self.event_resolved:
            for i, rect in enumerate(self.event_option_rects):
                if rect and rect.collidepoint(pos):
                    self._resolve_event_choice(i)
                    return
        else:
            if self.event_continue_rect and self.event_continue_rect.collidepoint(pos):
                audio.play("click")
                self._finish_node()

    # ═══════════════════════════════════════════════
    # SPIELSTART / NEUSTART
    # ═══════════════════════════════════════════════
    
    def _start_game(self):
        savegame.delete_save()   # Neuer Run verwirft alten Speicherstand
        self.player = Player()
        self.floor_num = 1
        self.turn_num = 1
        self.act = 1
        self.combat_log = []
        self.score_saved = False
        self.last_score = 0
        self.last_rank = None
        self.last_is_record = False
        self.gamemap = mapgen.generate(self.act)
        self.map_current = None
        self.current_node = None
        self.state = STATE_MAP
    
    def _restart(self):
        self.__init__(self.screen, self.clock)
    
    def _spawn_enemy(self, node_type="combat"):
        """Wählt einen Gegner passend zum Knotentyp und zur Tiefe"""
        import copy
        is_elite = (node_type == "elite")
        if node_type == "boss":
            enemy_def = random.choice([e for e in ENEMY_TYPES if e.get("is_boss")])
        elif is_elite:
            cands = [e for e in ENEMY_TYPES if e.get("tier", 1) <= 2 and not e.get("is_boss")]
            enemy_def = random.choice(cands)
        elif self.floor_num <= 3:
            cands = [e for e in ENEMY_TYPES if e.get("tier", 1) == 1]
            enemy_def = random.choice(cands)
        else:
            cands = [e for e in ENEMY_TYPES if e.get("tier", 1) <= 2 and not e.get("is_boss")]
            enemy_def = random.choice(cands)

        # Gegner skaliert mit der Tiefe (über Akte hinweg)
        enemy_def = copy.deepcopy(enemy_def)
        scale = 1.0 + (self.floor_num - 1) * 0.13
        enemy_def["hp"] = int(enemy_def["hp"] * scale)
        enemy_def["max_hp"] = enemy_def["hp"]
        enemy_def["damage"] = int(enemy_def["damage"] * scale)

        if is_elite:
            enemy_def["name"] = "⭐ Elite-" + enemy_def["name"]
            enemy_def["hp"] = int(enemy_def["hp"] * 1.4)
            enemy_def["max_hp"] = enemy_def["hp"]
            enemy_def["damage"] = int(enemy_def["damage"] * 1.25)
            enemy_def["armor"] = enemy_def.get("armor", 0) + 2
            enemy_def["is_elite"] = True

        self.enemy = Enemy(enemy_def)

    # ═══════════════════════════════════════════════
    # PFAD-/MAP-NAVIGATION
    # ═══════════════════════════════════════════════

    def _map_available(self):
        """Knoten, die der Spieler als nächstes betreten darf"""
        if not self.gamemap:
            return []
        if self.map_current is None:
            return mapgen.row0_nodes(self.gamemap)
        nm = mapgen.node_map(self.gamemap)
        cur = nm.get(tuple(self.map_current))
        return mapgen.next_nodes(self.gamemap, cur) if cur else []

    def _enter_node(self, node):
        """Betritt einen Knoten und startet den passenden Inhalt"""
        self.current_node = node
        audio.play("click")
        t = node["type"]
        if t in ("combat", "elite", "boss"):
            self._begin_combat(node)
        elif t == "event":
            self._open_event()
        elif t == "shop":
            self._open_shop()
        elif t == "rest":
            self.state = STATE_REST
        elif t == "treasure":
            relic = self._grant_random_relic()
            if relic:
                self.map_message = f"💠 Schatz: {relic['emoji']} {relic['name']}!"
            else:
                self.player.add_gold(40)
                self.map_message = "💰 Schatz: +40 Gold (alle Relikte schon da)!"
            self.map_message_timer = 2.5
            self._finish_node()

    def _begin_combat(self, node):
        """Startet einen Kampf an einem Karten-Knoten"""
        self.turn_num = 1
        self.floor_num = (self.act - 1) * mapgen.ROWS + node["row"] + 1
        self._spawn_enemy(node["type"])
        self._start_combat()

    def _finish_node(self):
        """Schließt den aktuellen Knoten ab und kehrt zur Karte zurück"""
        if self.current_node is not None:
            self.current_node["done"] = True
            self.map_current = [self.current_node["row"], self.current_node["col"]]
            was_boss = self.current_node["type"] == "boss"
            self.current_node = None
            if was_boss:
                self._next_act()
                return
        self.state = STATE_MAP

    def _next_act(self):
        """Nächster (härterer) Akt nach besiegtem Boss"""
        self.act += 1
        self.gamemap = mapgen.generate(self.act)
        self.map_current = None
        self.current_node = None
        self.map_message = f"🏔️ AKT {self.act} – es wird härter!"
        self.map_message_timer = 3.0
        audio.play("relic")
        self.state = STATE_MAP
    
    def _start_combat(self):
        self.state = STATE_PLAYER_TURN
        self.slot_machine = SlotMachine(420, 78)
        self.slot_done = False
        self.sub_phase = "cards"
        self.cards_played_this_turn = 0
        self.spins_remaining = 1 + (1 if self.player.has_relic("bonus_spin") else 0)
        self.slot_death_pending = False
        self.slot_death_timer = 0.0
        self.log_scroll = 0
        self._reset_combo()
        # Frische Starthand zu Kampfbeginn (alte Hand verfällt zwischen Kämpfen)
        self.player.discard.extend(self.player.hand)
        self.player.hand = []
        self.player.energy = self.player.max_energy
        self.player.block = 0
        self.player.next_free_card = self.player.has_relic("first_free")
        self.player.draw_initial_hand()
        self.damage_numbers = []
        self.slot_effects_shown = []
        self._log(f"--- Etage {self.floor_num}: {self.enemy.name} erscheint! ---")
        self._log(f"{self.enemy.tooltip}")

        # ─── Relik-Effekte zu Kampfbeginn ───
        self._apply_combat_start_relics()
    
    def _start_new_turn(self):
        """Neue Spieler-Runde"""
        self.turn_num += 1
        self.sub_phase = "cards"
        self.slot_done = False
        self.cards_played_this_turn = 0
        self.spins_remaining = 1 + self.player.bonus_spins
        if self.player.has_relic("bonus_spin"):
            self.spins_remaining += 1
        self.player.bonus_spins = 0
        # Gegner-Mechanik: Automat blockiert
        if self.enemy and self.enemy.jam_next:
            self.spins_remaining = max(0, self.spins_remaining - 1)
            self.enemy.jam_next = False
            self._log("🎰 Dein Automat ist blockiert! (−1 Dreh diese Runde)")
        self.player.start_turn()
        # Falsches Ass: erste Karte der Runde gratis
        if self.player.has_relic("first_free"):
            self.player.next_free_card = True
        self.slot_effects_shown = []
        self._reset_combo()
        self.state = STATE_PLAYER_TURN
        self._log(f"--- Runde {self.turn_num} ---")

    # ═══════════════════════════════════════════════
    # RELIKTE & COMBO – HELPER
    # ═══════════════════════════════════════════════

    def _apply_combat_start_relics(self):
        """Wendet Relik-Effekte an, die zu Kampfbeginn auslösen"""
        p = self.player
        if p.has_relic("start_block"):
            p.block += 12
            self._log("🛡️ Eiserner Wille: +12 Block!")
        if p.has_relic("combat_strength"):
            p.strength += 2
            self._log("🪖 Kriegsbanner: +2 Stärke!")
        if p.has_relic("interest"):
            bonus = min(10, p.gold // 25)
            if bonus > 0:
                p.add_gold(bonus)
                self._log(f"💰 Spardose: +{bonus} Gold Zinsen!")
        if p.has_relic("chicken_relic") and random.random() < 0.4:
            log = self.slot_machine._chicken_effect(p, self.enemy) if self.slot_machine else None
            self._log(f"🐔 Hühner-Totem: {log}" if log else "🐔 Hühner-Totem: Ein Huhn erscheint!")

    def _reset_combo(self):
        self.combo_type = None
        self.combo_count = 0

    def _bump_combo(self, card):
        """Aktualisiert die Combo und wendet Boni an. Gibt Log-Strings zurück."""
        logs = []
        if card.type == "curse":
            self._reset_combo()
            return logs
        if card.type == self.combo_type:
            self.combo_count += 1
        else:
            self.combo_type = card.type
            self.combo_count = 1

        if self.combo_count >= 2:
            self.combo_flash = 0.6
            audio.play_combo(self.combo_count)
            self._spawn_particles(600, 250, (255, 160, 40), count=10, speed=140, size=3)
            tier = self.combo_count - 1
            if card.type == "attack":
                bonus = tier * 4
                self.enemy.take_damage(bonus)
                logs.append(f"🔥 COMBO x{self.combo_count}: +{bonus} Bonus-Schaden!")
            elif card.type == "defense":
                bonus = tier * 4
                self.player.block += bonus
                logs.append(f"🔥 COMBO x{self.combo_count}: +{bonus} Bonus-Block!")
            elif card.type == "special":
                bonus = tier * 3
                self.player.add_gold(bonus)
                logs.append(f"🔥 COMBO x{self.combo_count}: +{bonus} Bonus-Gold!")
        return logs
    
    # ═══════════════════════════════════════════════
    # KARTEN SPIELEN
    # ═══════════════════════════════════════════════
    
    def _try_play_card(self, card):
        free = self.player.next_free_card
        cost = 0 if free else card.cost
        if cost > self.player.energy:
            self._log(f"❌ Nicht genug Energie für '{card.name}'! ({card.cost} nötig)")
            audio.play("error", 0.6)
            return
        if free:
            self.player.next_free_card = False
            self._log(f"✨ '{card.name}' gratis gespielt!")

        audio.play("card", 0.7)
        self.player.energy -= cost
        self.player.hand.remove(card)
        # Exhaust-Karten verschwinden für immer (nicht in den Abwurfstapel)
        if not card.exhaust:
            self.player.discard.append(card)

        # Snapshots für Effekt-Feedback
        e_hp0 = self.enemy.hp
        p_hp0 = self.player.hp
        blk0 = self.player.block
        gold0 = self.player.gold

        logs = self.resolver.resolve(card, self.player, self.enemy, self.slot_machine)
        for log in logs:
            self._log(log)

        if card.exhaust:
            self._log("   ♻️ Karte verbraucht und entfernt.")

        # Combo-System
        for log in self._bump_combo(card):
            self._log(log)

        # Münzregen: Gold pro gespielter Karte
        if self.player.coin_rain_active:
            self.player.add_gold(10)
            self._log("   🪙 Münzregen: +10 Gold!")

        # Bonus-Spins durch Karte?
        self.spins_remaining += self.player.bonus_spins
        self.player.bonus_spins = 0

        self.cards_played_this_turn += 1
        self.selected_card = None
        self.log_scroll = 0

        # Effekt-Feedback (Sound/Partikel/Shake) anhand der Deltas
        self._fx_enemy_hit(e_hp0 - self.enemy.hp)
        self._fx_block(self.player.block - blk0)
        if self.player.hp > p_hp0:
            self._fx_heal(self.player.hp - p_hp0)
        elif self.player.hp < p_hp0:
            self._fx_player_hit(p_hp0 - self.player.hp)  # Selbstschaden (Bombe etc.)
        self._fx_gold(self.player.gold - gold0)

        # Todescheck (berücksichtigt Lich-Undying)
        if self._enemy_is_down():
            self._enemy_defeated()

    def _enemy_is_down(self):
        """True nur, wenn der Gegner wirklich tot ist (Undying-Mechanik beachtet)"""
        if self.enemy.hp > 0:
            return False
        msg = self.enemy.try_undying()
        if msg:
            self._log(msg)
            audio.play("relic", 0.6)
            return False
        return True
    
    # ═══════════════════════════════════════════════
    # SLOT-PHASE
    # ═══════════════════════════════════════════════
    
    def _start_slot_phase(self):
        """Übergang zur Slot-Phase (Hand bleibt erhalten!)"""
        # Ungespielte Karten bleiben in der Hand für die nächste Runde.
        self.state = STATE_SLOT_SPIN
        self.slot_done = False
        self.slot_effects_shown = []
        self.log_scroll = 0
        self._reset_combo()
        audio.play("click")
        self._log("🎰 Zeit für den Spielautomaten!")

    def _do_spin(self):
        """Startet einen Spin"""
        if self.spins_remaining <= 0 or self.slot_machine.spinning:
            return

        self.spins_remaining -= 1
        self.player.slots_spun += 1
        # Gezinkte Würfel: immer Glück. Sonst Glücksrunden verbrauchen.
        lucky = self.player.has_relic("always_lucky") or self.player.lucky > 0
        if self.player.lucky > 0:
            self.player.lucky -= 1

        self.slot_machine.spin(lucky_bonus=lucky)
        self.slot_done = False
        self.slot_effects_shown = []
        audio.start_spin()
    
    def _process_slot_result(self):
        """Wertet Slot-Ergebnis aus"""
        audio.stop_spin()
        e_hp0 = self.enemy.hp
        names = [r["name"] for r in self.slot_machine.results] if self.slot_machine.results else []
        is_triple = len(names) == 3 and len(set(names)) == 1

        effects = self.slot_machine.evaluate(self.player, self.enemy)
        self.slot_effects_shown = effects
        for eff in effects:
            self._log(f"  {eff}")

        if is_triple:
            audio.play("jackpot")
            self._do_shake(12)
            self._spawn_particles(590, 150, (255, 210, 80), count=30, speed=240, size=5)
            self._spawn_particles(590, 150, (255, 120, 90), count=14, speed=200, size=4)
        self._fx_enemy_hit(e_hp0 - self.enemy.hp)

        if self._enemy_is_down():
            # Kurzer Delay, damit man das Slot-Ergebnis noch sehen kann (TODO #6)
            self.slot_death_pending = True
            self.slot_death_timer = 1.8
            self.slot_done = True
        else:
            self.slot_done = True
    
    # ═══════════════════════════════════════════════
    # GEGNER-RUNDE
    # ═══════════════════════════════════════════════
    
    def _start_enemy_turn(self):
        self.state = STATE_ENEMY_TURN
        self.enemy_turn_timer = 1.5  # Sekunden bis Angriff
        self.enemy_turn_log = []
        self._log("⚔️ Gegner ist am Zug...")
    
    def _update(self, dt):
        # Animationen laufen immer (auch während Hit-Stop)
        self._update_particles(dt)
        if self.shake > 0:
            self.shake = max(0.0, self.shake - dt * 60)
        if self.combo_flash > 0:
            self.combo_flash = max(0, self.combo_flash - dt)
        if self.map_message_timer > 0:
            self.map_message_timer -= dt
            if self.map_message_timer <= 0:
                self.map_message = ""
        self.damage_numbers = [(t, x, y, c, timer - dt)
                               for t, x, y, c, timer in self.damage_numbers
                               if timer - dt > 0]

        # Hit-Stop friert die Spiel-Logik kurz ein (Wucht-Gefühl)
        if self.hitstop > 0:
            self.hitstop = max(0.0, self.hitstop - dt)
            return

        if self.state == STATE_SLOT_SPIN:
            prev_done = sum(self.slot_machine._reel_done) if self.slot_machine else 0
            finished = self.slot_machine.update()
            now_done = sum(self.slot_machine._reel_done)
            if now_done > prev_done:
                audio.play("reel", 0.7)
            if finished and not self.slot_done:
                self._process_slot_result()
            if self.slot_death_pending:
                self.slot_death_timer -= dt
                if self.slot_death_timer <= 0:
                    self.slot_death_pending = False
                    self._enemy_defeated()

        elif self.state == STATE_ENEMY_TURN:
            self.enemy_turn_timer -= dt
            if self.enemy_turn_timer <= 0:
                self._execute_enemy_turn()

        elif self.state == STATE_SHOP:
            if self.shop_message_timer > 0:
                self.shop_message_timer -= dt
                if self.shop_message_timer <= 0:
                    self.shop_message = ""
    
    def _execute_enemy_turn(self):
        """Führt Gegner-Angriff aus"""
        hp_before = self.player.hp
        logs = self.enemy.execute_turn(self.player)
        for log in logs:
            self._log(log)

        dmg_taken = hp_before - self.player.hp
        self._fx_player_hit(dmg_taken)

        # Dornenpanzer-Relik: reflektiert pauschal 5 Schaden bei Gegnerangriff
        if self.player.has_relic("thorns") and dmg_taken > 0 and self.enemy.is_alive():
            thorn = self.enemy.take_damage(5)
            self._log(f"🌵 Dornenpanzer: {thorn} Schaden zurück!")

        # Reflektor: Spieler reflektiert erlittenen Schaden zurück
        if self.player.reflect:
            if dmg_taken > 0:
                reflected = self.enemy.take_damage(dmg_taken)
                self._log(f"🪞 Reflektor wirft {reflected} Schaden zurück!")
            self.player.reflect = False

        # Gegner durch Reflektion/Dornen/eigenen Burn gestorben?
        if self._enemy_is_down():
            self._enemy_defeated()
            return

        if not self.player.is_alive():
            self.state = STATE_GAME_OVER
            self._save_highscore()
            audio.stop_spin()
            audio.play("lose")
            self._log("💀 Du bist gestorben. Schade.")
        else:
            self._start_new_turn()
    
    # ═══════════════════════════════════════════════
    # SIEG / BELOHNUNG
    # ═══════════════════════════════════════════════
    
    def _enemy_defeated(self):
        """Gegner besiegt: Belohnung vorbereiten"""
        self.player.damage_dealt += self.enemy.max_hp
        self.player.enemies_defeated += 1

        # Goldener Finger: +30% Gold
        gold = self.enemy.get_gold_reward()
        if self.player.has_relic("gold_boost"):
            gold = int(gold * 1.3)
        self.gold_reward = gold
        self.player.add_gold(gold)
        self._log(f"🏆 {self.enemy.name} besiegt! +{gold} Gold!")
        audio.play("gold", 0.7)
        self._spawn_particles(*self.ENEMY_FX, color=(255, 210, 80), count=22, speed=200, size=4)

        # Herzstein: Heilung bei Kill
        if self.player.has_relic("heal_on_kill"):
            healed = self.player.heal_hp(8)
            if healed > 0:
                self._log(f"❤️ Herzstein: +{healed} HP!")

        # Relikt-Belohnung bei Elite & Boss
        self.reward_relic = None
        if self.enemy.is_elite or self.enemy.is_boss:
            relic = self._grant_random_relic()
            if relic:
                self.reward_relic = relic
                self._log(f"💠 Relikt erhalten: {relic['emoji']} {relic['name']}!")

        # Drei Karten zur Wahl – nach Seltenheit gewichtet (keine Flüche)
        self.reward_cards = self._weighted_reward_cards(3)

        self.state = STATE_REWARD

    def _weighted_reward_cards(self, n=3):
        """Wählt n verschiedene Karten gewichtet nach Seltenheit aus"""
        boss = bool(self.enemy and (self.enemy.is_elite or self.enemy.is_boss))
        weights = {
            "common":   40 if boss else 68,
            "uncommon": 38 if boss else 27,
            "rare":     22 if boss else 5,
        }
        avail = list(CARD_DEFINITIONS)  # Flüche sind separat, nicht enthalten
        chosen = []
        for _ in range(min(n, len(avail))):
            ws = [weights.get(c.get("rarity", "common"), 10) for c in avail]
            pick = random.choices(avail, weights=ws, k=1)[0]
            chosen.append(pick)
            avail.remove(pick)
        return [Card(c) for c in chosen]

    def _grant_random_relic(self):
        """Vergibt ein zufälliges noch nicht besessenes Relikt"""
        owned = {r["id"] for r in self.player.relics}
        available = [r for r in RELIC_DEFINITIONS if r["id"] not in owned]
        if not available:
            return None
        relic = random.choice(available)
        self.player.add_relic(relic)
        audio.play("relic")
        return relic

    def _pick_reward_card(self, idx):
        """Spieler wählt eine Belohnungskarte"""
        if idx < len(self.reward_cards):
            card = self.reward_cards[idx]
            # Die bereits erzeugte Karten-Instanz direkt ins Deck legen
            self.player.discard.append(card)
            self._log(f"📦 Karte hinzugefügt: {card.name}!")
        self._after_reward()

    def _skip_reward(self):
        """Belohnung überspringen"""
        self._after_reward()

    def _after_reward(self):
        """Nach der Belohnung zurück zur Karte (Boss -> nächster Akt)"""
        self._finish_node()
    
    # ═══════════════════════════════════════════════
    # EVENTS
    # ═══════════════════════════════════════════════

    def _open_event(self):
        """Öffnet ein zufälliges Event"""
        self.current_event = random.choice(EVENT_DEFINITIONS)
        self.event_resolved = False
        self.event_result = ""
        self.event_option_rects = []
        self.event_continue_rect = None
        self.hovered_event_idx = None
        self.state = STATE_EVENT

    def _resolve_event_choice(self, idx):
        """Wertet die gewählte Event-Option aus"""
        if not self.current_event or idx >= len(self.current_event["options"]):
            return
        audio.play("click")
        opt = self.current_event["options"][idx]
        eff = opt["effect"]
        val = opt.get("value", 0)
        p = self.player
        msg = ""

        if eff == "gold":
            p.add_gold(val); msg = f"+{val} Gold erhalten."
        elif eff == "lose_gold":
            lost = min(val, p.gold); p.gold -= lost; msg = f"-{lost} Gold verloren."
        elif eff == "heal":
            h = p.heal_hp(val); msg = f"+{h} HP geheilt."
        elif eff == "damage":
            p.take_damage(val, ignore_block=True); msg = f"-{val} HP. Autsch."
        elif eff == "max_hp":
            p.max_hp += val; p.hp += val; msg = f"+{val} Max HP!"
        elif eff == "strength":
            p.strength += val; msg = f"+{val} Stärke dauerhaft!"
        elif eff == "energy":
            p.max_energy += 1; msg = "+1 Max Energie!"
        elif eff == "spins":
            p.lucky += val; msg = f"+{val} Glücksrunden!"
        elif eff == "relic":
            r = self._grant_random_relic()
            msg = f"Relikt erhalten: {r['emoji']} {r['name']}!" if r else "Du hast schon alle Relikte!"
        elif eff == "relic_for_hp":
            p.take_damage(val, ignore_block=True)
            r = self._grant_random_relic()
            msg = f"-{val} HP. Relikt: {r['emoji']} {r['name']}!" if r else f"-{val} HP, aber kein Relikt mehr übrig."
        elif eff == "relic_for_gold":
            if p.gold >= val:
                p.spend_gold(val)
                r = self._grant_random_relic()
                msg = f"-{val} Gold. Relikt: {r['emoji']} {r['name']}!" if r else f"-{val} Gold, aber kein Relikt mehr übrig."
            else:
                msg = "Nicht genug Gold dafür!"
        elif eff == "sacrifice":
            p.take_damage(10, ignore_block=True); p.strength += 2
            msg = "-10 HP, +2 Stärke dauerhaft."
        elif eff == "loot_cursed":
            p.add_gold(val); self._add_curse()
            msg = f"+{val} Gold... aber ein Fluch schleicht sich ins Deck."
        elif eff == "feed_chicken":
            if p.gold >= val:
                p.spend_gold(val); p.max_hp += 15; p.hp += 15
                msg = f"-{val} Gold, +15 Max HP! Das Huhn ist zufrieden."
            else:
                msg = "Nicht genug Gold zum Füttern!"
        elif eff == "chicken":
            log = self.slot_machine._chicken_effect(p, self.enemy) if (self.slot_machine and self.enemy) else None
            msg = log or "Ein Huhn erscheint und verschwindet wieder."
        elif eff == "threaten":
            if random.random() < 0.5:
                p.add_gold(40); msg = "Er knickt ein! +40 Gold."
            else:
                self._add_curse(); msg = "Er verflucht dich! Ein Fluch im Deck."
        elif eff == "hack_atm":
            if random.random() < 0.5:
                p.add_gold(50); msg = "Hack erfolgreich! +50 Gold."
            else:
                p.take_damage(15, ignore_block=True); msg = "STROMSCHLAG! -15 HP."
        elif eff == "deposit":
            gain = min(30, p.gold); p.add_gold(gain)
            msg = f"Verdoppelt: +{gain} Gold."
        elif eff == "break_chest":
            p.take_damage(8, ignore_block=True); p.add_gold(val)
            msg = f"-8 HP, dafür +{val} Gold!"
        elif eff == "nothing":
            msg = "Du gehst weiter. Nichts passiert."
        else:
            msg = "..."

        self._log(f"❓ {self.current_event['title']}: {msg}")
        self.event_result = msg
        self.event_resolved = True

    def _add_curse(self):
        """Fügt eine zufällige Fluch-Karte zum Deck hinzu"""
        curse = random.choice(CURSE_DEFINITIONS)
        self.player.add_card_to_deck(curse)
        self._log(f"💀 Fluch erhalten: {curse['name']}!")

    # ═══════════════════════════════════════════════
    # SHOP
    # ═══════════════════════════════════════════════

    def _open_shop(self):
        """Öffnet den Shop zwischen den Etagen (Endlos-Modus)"""
        self.state = STATE_SHOP
        self.shop_remove_mode = False
        self.shop_upgrade_mode = False
        self.shop_message = ""
        self.shop_message_timer = 0.0
        self.shop_purchased = set()   # bereits gekaufte Item-IDs (pro Shop-Besuch)

        # Schmiede ist immer verfügbar + 4 zufällige feste Items
        forge = {"id": "upgrade_card", "name": "Schmiede", "emoji": "⚒️", "cost": 50,
                 "desc": "Werte eine Karte dauerhaft auf (+50% Werte)."}
        available = SHOP_FIXED_ITEMS[:]
        random.shuffle(available)
        self.shop_items = [forge] + available[:4]
    
    def _shop_message(self, text):
        self.shop_message = text
        self.shop_message_timer = 2.0
    
    def _buy_shop_item(self, item):
        """Kauft ein Shop-Item (jedes nur 1x pro Shop-Besuch)"""
        item_id = item["id"]
        cost = item["cost"]

        if item_id in self.shop_purchased:
            self._shop_message("❌ Schon gekauft!")
            audio.play("error", 0.6)
            return
        if self.player.gold < cost:
            self._shop_message("❌ Nicht genug Gold!")
            audio.play("error", 0.6)
            return
        audio.play("click")

        # "Karte entfernen" braucht eine zweite Auswahl
        if item_id == "remove_card":
            if len([c for c in self.player.deck + self.player.discard]) <= 5:
                self._shop_message("❌ Dein Deck ist schon klein genug!")
                return
            self.shop_remove_mode = True
            self.shop_pending_cost = cost
            return

        # "Karte aufwerten" (Schmiede) braucht eine zweite Auswahl
        if item_id == "upgrade_card":
            upgradeable = [c for c in self.player.deck + self.player.discard + self.player.hand
                           if c.can_upgrade()]
            if not upgradeable:
                self._shop_message("❌ Keine aufwertbare Karte im Deck!")
                return
            self.upgrade_ctx = "shop"
            self.shop_upgrade_mode = True
            self.shop_pending_cost = cost
            return

        # Sonst direkt anwenden
        self.player.spend_gold(cost)
        self._apply_shop_item(item_id)
        self.shop_purchased.add(item_id)
    
    def _apply_shop_item(self, item_id):
        """Wendet den gekauften Effekt an"""
        p = self.player
        if item_id == "heal_full":
            healed = p.heal_hp(p.max_hp)
            self._shop_message(f"❤️ Vollheilung! +{healed} HP")
        elif item_id == "heal_half":
            healed = p.heal_hp(30)
            self._shop_message(f"🩹 +{healed} HP geheilt")
        elif item_id == "max_hp":
            p.max_hp += 15
            p.hp += 15
            self._shop_message("💪 +15 Max HP!")
        elif item_id == "strength":
            p.strength += 2
            self._shop_message("⚡ +2 Stärke!")
        elif item_id == "max_energy":
            p.max_energy += 1
            self._shop_message("🔋 +1 Max Energie!")
        elif item_id == "extra_spin":
            p.lucky += 2
            self._shop_message("🎰 +2 Glücksrunden!")
    
    def _remove_card_from_deck(self, card):
        """Entfernt die gewählte Karte (im Karte-verbrennen-Modus)"""
        removed = False
        if card in self.player.deck:
            self.player.deck.remove(card)
            removed = True
        elif card in self.player.discard:
            self.player.discard.remove(card)
            removed = True
        
        if removed:
            self.player.spend_gold(self.shop_pending_cost)
            self.shop_purchased.add("remove_card")
            self._shop_message(f"🔥 '{card.name}' verbrannt!")
        self.shop_remove_mode = False

    def _upgrade_card_in_deck(self, card):
        """Wertet die gewählte Karte auf (Schmiede – Shop oder Lagerfeuer)"""
        if card.can_upgrade():
            old_name = card.name
            card.upgrade()
            audio.play("relic", 0.7)
            if self.upgrade_ctx == "shop":
                self.player.spend_gold(self.shop_pending_cost)
                self.shop_purchased.add("upgrade_card")
                self._shop_message(f"⚒️ '{old_name}' aufgewertet!")
            else:
                self.map_message = f"⚒️ '{old_name}' aufgewertet!"
                self.map_message_timer = 2.5
        else:
            audio.play("error", 0.6)
        self.shop_upgrade_mode = False
        if self.upgrade_ctx == "rest":
            self.upgrade_ctx = None
            self._finish_node()
        else:
            self.upgrade_ctx = None
    
    def _gamble(self):
        """Slot-Gambling im Shop: Setze 25 Gold, Glücksrad-Auszahlung"""
        bet = 25
        if self.player.gold < bet:
            self._shop_message("❌ Mindesteinsatz 25 Gold!")
            return
        
        self.player.spend_gold(bet)
        audio.play("reel", 0.8)
        roll = random.random()
        # Auszahltabelle: meistens Verlust, selten großer Gewinn
        if roll < 0.40:
            self._shop_message("🎰 NICHTS. Das Haus gewinnt. (−25 Gold)")
        elif roll < 0.65:
            win = bet  # Einsatz zurück
            self.player.add_gold(win)
            self._shop_message(f"🎰 Einsatz zurück (+{win} Gold)")
        elif roll < 0.85:
            win = bet * 2
            self.player.add_gold(win)
            self._shop_message(f"🎰 GEWINN! +{win} Gold (2x)")
        elif roll < 0.96:
            win = bet * 4
            self.player.add_gold(win)
            self._shop_message(f"🎰 GROSSER GEWINN! +{win} Gold (4x)!")
        else:
            win = bet * 10
            self.player.add_gold(win)
            self._shop_message(f"🎰💰 JACKPOT!!! +{win} Gold (10x)!!!")
            audio.play("jackpot")
            self._spawn_particles(self.shop_gamble_rect.centerx if self.shop_gamble_rect else 300,
                                  430, (255, 210, 80), count=26, speed=220, size=4)
    
    def _leave_shop(self):
        """Verlässt den Shop, zurück zur Karte"""
        self.shop_remove_mode = False
        self.shop_upgrade_mode = False
        audio.play("click")
        self._finish_node()
    
    def _next_floor(self):
        """Zur nächsten Etage (endlos)"""
        self.floor_num += 1
        self.turn_num = 1
        self._spawn_enemy()
        self._start_combat()
    
    def _win_game(self):
        """Spiel gewonnen"""
        self.state = STATE_VICTORY
        self._save_highscore(won=True)
        audio.stop_spin()
        audio.play("win")
    
    def _save_highscore(self, won=False):
        """Speichert den Punktestand (nur einmal pro Run)"""
        if self.score_saved:
            return
        self.last_rank, self.last_score, self.last_is_record = add_highscore(
            self.player, self.floor_num, won=won)
        self.highscores = load_highscores()
        self.score_saved = True
        savegame.delete_save()   # Run beendet -> Speicherstand entfernen

    # ═══════════════════════════════════════════════
    # SPEICHERN / LADEN
    # ═══════════════════════════════════════════════

    def _serialize_card(self, c):
        return {
            "name": c.name, "type": c.type, "cost": c.cost,
            "damage": c.damage, "block": c.block, "heal": c.heal,
            "color": list(c.color), "tooltip": c.tooltip,
            "rarity": c.rarity, "effect": c.effect,
            "exhaust": c.exhaust, "upgraded": c.upgraded,
        }

    def _deserialize_card(self, d):
        card = Card(d)            # Card.__init__ liest alle nötigen Felder
        card.upgraded = d.get("upgraded", False)
        return card

    def _serialize_player(self, p):
        return {
            "max_hp": p.max_hp, "hp": p.hp, "gold": p.gold, "block": p.block,
            "energy": p.energy, "max_energy": p.max_energy,
            "burn": p.burn, "strength": p.strength, "lucky": p.lucky,
            "shield_up": p.shield_up, "reflect": p.reflect,
            "coin_rain_active": p.coin_rain_active, "next_free_card": p.next_free_card,
            "total_damage_taken": p._total_damage_taken, "bonus_spins": p.bonus_spins,
            "deck": [self._serialize_card(c) for c in p.deck],
            "hand": [self._serialize_card(c) for c in p.hand],
            "discard": [self._serialize_card(c) for c in p.discard],
            "relics": [dict(r) for r in p.relics],
            "stats": {
                "damage_dealt": p.damage_dealt, "gold_earned": p.gold_earned,
                "slots_spun": p.slots_spun, "chickens_summoned": p.chickens_summoned,
                "enemies_defeated": p.enemies_defeated,
            },
        }

    def _deserialize_player(self, d):
        p = Player()  # baut Starterdeck – wird gleich überschrieben
        p.max_hp = d["max_hp"]; p.hp = d["hp"]; p.gold = d["gold"]; p.block = d["block"]
        p.energy = d["energy"]; p.max_energy = d["max_energy"]
        p.burn = d["burn"]; p.strength = d["strength"]; p.lucky = d["lucky"]
        p.shield_up = d["shield_up"]; p.reflect = d["reflect"]
        p.coin_rain_active = d["coin_rain_active"]; p.next_free_card = d["next_free_card"]
        p._total_damage_taken = d.get("total_damage_taken", 0)
        p.bonus_spins = d.get("bonus_spins", 0)
        p.deck = [self._deserialize_card(c) for c in d["deck"]]
        p.hand = [self._deserialize_card(c) for c in d["hand"]]
        p.discard = [self._deserialize_card(c) for c in d["discard"]]
        p.relics = [dict(r) for r in d["relics"]]
        st = d.get("stats", {})
        p.damage_dealt = st.get("damage_dealt", 0)
        p.gold_earned = st.get("gold_earned", 0)
        p.slots_spun = st.get("slots_spun", 0)
        p.chickens_summoned = st.get("chickens_summoned", 0)
        p.enemies_defeated = st.get("enemies_defeated", 0)
        return p

    def _serialize_enemy(self, e):
        return {
            "name": e.name, "hp": e.hp, "max_hp": e.max_hp, "damage": e.damage,
            "armor": e.armor, "block": e.block, "gold_reward": list(e.gold_reward),
            "color": list(e.color), "tooltip": e.tooltip, "tier": e.tier,
            "is_boss": e.is_boss, "is_elite": e.is_elite, "mechanic": e.mechanic,
            "asset": e.asset,
            "burn": e.burn, "weakened": e.weakened,
            "intent": e.intent, "intent_value": e.intent_value,
            "undying_used": e._undying_used, "jam_next": e.jam_next,
            "turn_count": e.turn_count,
        }

    def _deserialize_enemy(self, d):
        etype = {
            "name": d["name"], "hp": d["hp"], "max_hp": d["max_hp"],
            "damage": d["damage"], "armor": d["armor"],
            "gold_reward": tuple(d["gold_reward"]), "color": tuple(d["color"]),
            "tooltip": d["tooltip"], "tier": d["tier"],
            "is_boss": d["is_boss"], "is_elite": d["is_elite"],
            "mechanic": d.get("mechanic"), "asset": d.get("asset"),
        }
        e = Enemy(etype)
        e.block = d["block"]; e.burn = d["burn"]; e.weakened = d["weakened"]
        e.intent = d["intent"]; e.intent_value = d["intent_value"]
        e._undying_used = d.get("undying_used", False)
        e.jam_next = d.get("jam_next", False)
        e.turn_count = d.get("turn_count", 0)
        return e

    def _serialize_run(self):
        in_combat = bool(self.enemy and self.enemy.is_alive())
        cn = None
        if self.current_node is not None:
            cn = [self.current_node["row"], self.current_node["col"]]
        return {
            "floor_num": self.floor_num,
            "turn_num": self.turn_num,
            "act": self.act,
            "resume": "combat" if in_combat else "map",
            "spins_remaining": self.spins_remaining,
            "player": self._serialize_player(self.player),
            "enemy": self._serialize_enemy(self.enemy) if in_combat else None,
            "gamemap": self.gamemap,
            "map_current": self.map_current,
            "current_node": cn,
            "log": self.combat_log[-40:],
        }

    def _save_and_quit(self):
        """Speichert den laufenden Run und beendet das Spiel"""
        if self.player:
            savegame.write_save(self._serialize_run())
        self.running = False

    def _load_run(self):
        """Lädt einen gespeicherten Run (nur falls versionskompatibel)"""
        data = savegame.load_save()
        if not data:
            return
        self.player = self._deserialize_player(data["player"])
        self.floor_num = data.get("floor_num", 1)
        self.turn_num = data.get("turn_num", 1)
        self.act = data.get("act", 1)
        self.combat_log = list(data.get("log", []))
        self.score_saved = False
        self.last_score = 0
        self.last_rank = None
        self.last_is_record = False

        # Karte wiederherstellen (Fallback: neu generieren)
        self.gamemap = data.get("gamemap") or mapgen.generate(self.act)
        self.map_current = data.get("map_current")

        if data.get("resume") == "combat" and data.get("enemy"):
            cn = data.get("current_node")
            self.current_node = (mapgen.node_map(self.gamemap).get(tuple(cn))
                                 if (cn and self.gamemap) else None)
            self.enemy = self._deserialize_enemy(data["enemy"])
            self._resume_combat(data.get("spins_remaining", 1))
        else:
            # Zwischen den Knoten gespeichert -> zurück zur Karte
            self.current_node = None
            self.enemy = None
            self.state = STATE_MAP

    def _resume_combat(self, spins_remaining):
        """Setzt einen Kampf fort (Hand/Energie/Block bleiben wie gespeichert)"""
        self.state = STATE_PLAYER_TURN
        self.slot_machine = SlotMachine(420, 78)
        self.slot_done = False
        self.sub_phase = "cards"
        self.cards_played_this_turn = 0
        self.spins_remaining = spins_remaining
        self.slot_death_pending = False
        self.slot_death_timer = 0.0
        self.log_scroll = 0
        self._reset_combo()
        self.damage_numbers = []
        self.slot_effects_shown = []
        self._log("💾 Spielstand geladen – weiter geht's!")
    
    # ═══════════════════════════════════════════════
    # LOG-HELPER
    # ═══════════════════════════════════════════════
    
    def _log(self, text):
        self.combat_log.append(text)
        if len(self.combat_log) > 100:
            self.combat_log = self.combat_log[-100:]
    
    def _add_damage_number(self, text, x, y, color):
        self.damage_numbers.append((text, x, y, color, 1.5))

    # ═══════════════════════════════════════════════
    # JUICE: Shake, Hit-Stop, Partikel
    # ═══════════════════════════════════════════════

    def _do_shake(self, amount):
        if not self.options.get("shake", True):
            return
        self.shake = min(16.0, max(self.shake, amount))

    def _do_hitstop(self, dur):
        self.hitstop = max(self.hitstop, dur)

    def _spawn_particles(self, x, y, color, count=12, speed=180, life=0.5,
                         size=4, gravity=420, spread=2 * 3.14159, dir0=0.0):
        if not self.options.get("particles", True):
            return
        for _ in range(count):
            ang = dir0 + random.uniform(-spread / 2, spread / 2)
            sp = speed * random.uniform(0.4, 1.0)
            vx = sp * math.cos(ang)
            vy = sp * math.sin(ang) - random.uniform(0, speed * 0.3)
            lf = life * random.uniform(0.6, 1.0)
            self.particles.append([x, y, vx, vy, lf, lf, color, size, gravity])

    def _update_particles(self, dt):
        alive = []
        for p in self.particles:
            p[4] -= dt
            if p[4] <= 0:
                continue
            p[0] += p[2] * dt
            p[1] += p[3] * dt
            p[3] += p[8] * dt   # gravity
            alive.append(p)
        self.particles = alive

    def _draw_particles(self):
        for x, y, vx, vy, life, maxlife, color, size, grav in self.particles:
            a = max(0.0, min(1.0, life / maxlife))
            s = max(1, int(size * a))
            surf = pygame.Surface((s * 2, s * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*color, int(230 * a)), (s, s), s)
            self.screen.blit(surf, (int(x - s), int(y - s)))

    # Bildschirm-Ankerpunkte für Effekte
    ENEMY_FX = (200, 220)
    PLAYER_FX = (120, 36)

    def _fx_enemy_hit(self, dmg):
        """Treffer am Gegner: Sound, Partikel, Shake, Hit-Stop, Schadenszahl"""
        if dmg <= 0:
            return
        audio.play("hit", min(1.0, 0.5 + dmg / 60))
        x, y = self.ENEMY_FX
        self._spawn_particles(x, y, (255, 90, 60), count=min(30, 8 + dmg // 2),
                              speed=150 + dmg * 3, size=4)
        self._spawn_particles(x, y, (255, 205, 90), count=6, speed=120, size=3)
        self._do_shake(min(14.0, 3 + dmg * 0.18))
        self._do_hitstop(min(0.13, 0.02 + dmg * 0.0026))
        self._add_damage_number(f"-{dmg}", x + 12, y - 36, (255, 120, 90))

    def _fx_player_hit(self, dmg):
        if dmg <= 0:
            return
        audio.play("hit", min(1.0, 0.5 + dmg / 60))
        x, y = self.PLAYER_FX
        self._spawn_particles(150, 18, (255, 70, 70), count=min(24, 6 + dmg // 2),
                              speed=130 + dmg * 2, size=4)
        self._do_shake(min(13.0, 3 + dmg * 0.2))
        self._do_hitstop(min(0.1, 0.02 + dmg * 0.002))
        self._add_damage_number(f"-{dmg}", 150, 26, (255, 90, 90))

    def _fx_block(self, amount):
        if amount <= 0:
            return
        audio.play("block", 0.7)
        self._spawn_particles(150, 24, (90, 160, 230), count=8, speed=120, size=3)

    def _fx_heal(self, amount):
        if amount <= 0:
            return
        audio.play("heal", 0.7)
        self._spawn_particles(150, 24, (80, 220, 120), count=10, speed=130, size=3)
        self._add_damage_number(f"+{amount}", 150, 26, (90, 230, 130))

    def _fx_gold(self, amount):
        if amount <= 0:
            return
        audio.play("gold", 0.6)
        self._spawn_particles(270, 50, (255, 210, 80), count=8, speed=120, size=3)

    # ═══════════════════════════════════════════════
    # SCHADENS-VORSCHAU (beim Hovern)
    # ═══════════════════════════════════════════════

    def _simulate_damage(self, raw_hits):
        """Simuliert Rüstung + Block des Gegners, gibt effektiven Gesamtschaden zurück"""
        armor = self.enemy.armor
        block = self.enemy.block
        total = 0
        for raw in raw_hits:
            eff = max(0, raw - armor)
            absorbed = min(block, eff)
            block -= absorbed
            eff -= absorbed
            total += eff
        return total

    def _preview_damage(self, card):
        """Voraussichtlicher Schaden einer Karte – nur für deterministische Effekte."""
        if not self.enemy:
            return None
        p, e = self.player, self.enemy
        s = p.strength
        eff = card.effect
        if eff in ("damage", "lifesteal", "annihilate"):
            hits = [card.damage + s]
        elif eff == "nuke":
            hits = [card.damage + s * 2]
        elif eff == "double_strike":
            hits = [card.damage + s, card.damage + s]
        elif eff == "execrate":
            hits = [e.max_hp // 3 + s]
        elif eff == "rage":
            hits = [(p.max_hp - p.hp) * 2 + s]
        elif eff == "iron_storm":
            hits = [max(0, p.block) + s]
        elif eff == "retribution":
            hits = [max(5, p._total_damage_taken // 10) + s]
        elif eff == "tax_evasion":
            hits = [max(5, p.gold // 10) + card.damage + s]
        elif eff == "bribe":
            hits = [30 + s] if p.gold >= 20 else None
        elif eff == "all_in":
            hits = [p.gold + s] if p.gold > 0 else None
        else:
            return None  # zufällige/bedingte Effekte: keine Vorschau
        if hits is None:
            return None
        return self._simulate_damage(hits)

    def _preview_heal(self, card):
        """Voraussichtliche Heilung einer Karte (tatsächlich, bis Max-HP)."""
        p = self.player
        eff = card.effect
        if eff in ("heal", "lifesteal"):
            raw = card.heal
        elif eff == "second_wind":
            raw = (p.max_hp - p.hp) // 4
        elif eff == "last_resort":
            raw = p.max_hp - p.hp
        else:
            return 0
        return max(0, min(raw, p.max_hp - p.hp))

    def _incoming_damage(self):
        """HP-Verlust beim nächsten Gegnerangriff (nach Block). 0 wenn kein Angriff."""
        e = self.enemy
        if not e or not e.is_alive() or e.intent not in ("attack", "heavy_attack"):
            return 0
        dmg = e.intent_value
        if e.weakened > 0:
            dmg //= 2
        return max(0, dmg - self.player.block)

    # ═══════════════════════════════════════════════
    # DRAW
    # ═══════════════════════════════════════════════
    
    def _draw(self):
        if self.state == STATE_MENU:
            self.ui.draw_main_menu(self._compute_menu_layout())

        elif self.state == STATE_TUTORIAL:
            self.ui.draw_tutorial()

        elif self.state == STATE_CHANGELOG:
            self.ui.draw_changelog(CHANGELOG)

        elif self.state == STATE_OPTIONS:
            self.ui.draw_options(self._compute_options_layout(), self.options)

        elif self.state == STATE_PAUSE:
            self.ui.draw_pause(self._compute_pause_layout())

        elif self.state == STATE_MAP:
            self.ui.draw_map(self.gamemap, self.map_current, self._map_available(),
                             self.hovered_node, self.player, self.act, self.map_message)

        elif self.state == STATE_REST:
            self.ui.draw_rest(self.player, self._compute_rest_layout())

        elif self.state in (STATE_PLAYER_TURN, STATE_SLOT_SPIN, STATE_ENEMY_TURN):
            self._draw_combat()
        
        elif self.state == STATE_REWARD:
            self._draw_combat_bg()  # Hintergrund
            self._draw_reward()

        elif self.state == STATE_EVENT:
            self._draw_event()

        elif self.state == STATE_SHOP:
            self._draw_shop()
        
        elif self.state == STATE_SCORES:
            self._draw_scores()
        
        elif self.state == STATE_GAME_OVER:
            self.ui.draw_game_over(self.player, self.floor_num,
                                   self.last_score, self.last_rank)

        elif self.state == STATE_VICTORY:
            self.ui.draw_victory(self.player, self.last_score, self.last_rank)

        # Globale Overlays (Schmiede/Verbrennen) über dem aktuellen Screen
        if self.shop_remove_mode:
            self.shop_remove_rects = self.ui.draw_card_grid(
                self.player, "🔥 Welche Karte verbrennen?", ORANGE, only_upgradeable=False)
        elif self.shop_upgrade_mode:
            self.shop_upgrade_rects = self.ui.draw_card_grid(
                self.player, "⚒️ Welche Karte aufwerten?", GOLD, only_upgradeable=True)

        # Partikel über allem
        self._draw_particles()
        # Mute-Indikator
        if audio.is_muted():
            self.ui._text("🔇", self.ui.font_small, GREY, SCREEN_W - 30, 6)
    
    def _draw_combat_bg(self):
        """Zeichnet den Kampf-Hintergrund ohne UI-Elemente"""
        self.ui.draw_background()
    
    def _draw_combat(self):
        """Hauptkampf-Bildschirm"""
        self.ui.draw_background()

        # Status-Leiste oben
        self.ui.draw_status_bar(self.player, self.enemy, self.floor_num, self.turn_num)

        # Gegner (links-mitte)
        if self.enemy:
            self.ui.draw_enemy(self.enemy, 50, 82, 300, 280)

        # Reliktleiste NACH dem Gegner -> Hover-Tooltip liegt über dem Sprite
        self.ui.draw_relic_bar(self.player, 8, 84)

        # Slot-Maschine nur in Slot-Phase (TODO #8)
        if self.state == STATE_SLOT_SPIN and self.slot_machine:
            self.slot_machine.draw(self.screen,
                                   self.ui.font_title, self.ui.font_large,
                                   self.ui.font_small, self.ui.font_tiny)

        # Slot-Effekte nur in Slot-Phase
        if self.state == STATE_SLOT_SPIN and self.slot_effects_shown:
            self._draw_slot_effects()

        # Kampf-Log (mit Scroll)
        self.ui.draw_combat_log(self.combat_log, 420, 290, 380, 195, scroll=self.log_scroll)
        
        # Phasen-spezifische UI
        if self.state == STATE_PLAYER_TURN:
            self._draw_player_turn_ui()
        elif self.state == STATE_SLOT_SPIN:
            self._draw_slot_ui()
        elif self.state == STATE_ENEMY_TURN:
            self._draw_enemy_turn_ui()
        
        # Schaden-Nummern
        for text, x, y, color, timer in self.damage_numbers:
            offset = int((1.5 - timer) * 60)
            self.ui.draw_damage_number(text, x, y, color, offset)
    
    def _draw_player_turn_ui(self):
        """UI für Spieler-Karten-Phase"""
        # Phase-Anzeige
        phase_txt = self.ui.font_title.render("⚔️ DEIN ZUG — Spiele Karten!", True, CYAN)
        self.screen.blit(phase_txt, (SCREEN_W//2 - phase_txt.get_width()//2, 488))

        # Combo-Anzeige
        if self.combo_count >= 2 and self.combo_type:
            self.ui.draw_combo_badge(self.combo_count, self.combo_type, self.combo_flash)

        # Schadens-/Heilungs-Vorschau für gehoverte Karte
        heal_prev = 0
        if (self.hovered_card_idx is not None
                and 0 <= self.hovered_card_idx < len(self.player.hand)):
            card = self.player.hand[self.hovered_card_idx]
            if self.enemy:
                dmg = self._preview_damage(card)
                if dmg is not None and dmg > 0:
                    self.ui.draw_damage_preview(self.enemy, dmg)
                    ex, ey = self.ENEMY_FX
                    self.ui._text(f"-{dmg}", self.ui.font_h1, (255, 130, 100),
                                  ex, ey - 96, center=True, shadow=True)
            heal_prev = self._preview_heal(card)

        # Eigene HP: Heilungs-Vorschau (grün) + eingehender Schaden (rot)
        self.ui.draw_player_hp_preview(self.player, heal_prev, self._incoming_damage())

        # Handkarten
        self.card_rects = self.ui.draw_hand(
            self.player.hand,
            selected_card=self.selected_card,
            hovered_idx=self.hovered_card_idx
        )
        
        # "Slot-Phase"-Button (= Runde beenden)
        btn_x, btn_y, btn_w, btn_h = SCREEN_W - 170, SCREEN_H//2 - 25, 160, 50
        self.ui.draw_button("🎰 Slot drehen", btn_x, btn_y, btn_w, btn_h,
                           color=GOLD, pulsing=True)
        
        # Energie-Anzeige
        energy_dots = ""
        for i in range(self.player.max_energy):
            energy_dots += "⚡" if i < self.player.energy else "○"
        e_txt = self.ui.font_medium.render(energy_dots, True, CYAN)
        self.screen.blit(e_txt, (SCREEN_W//2 - e_txt.get_width()//2, 515))
        
        # Deck-Info
        deck_txt = self.ui.font_tiny.render(
            f"Deck: {len(self.player.deck)} | Abwurf: {len(self.player.discard)}",
            True, GREY)
        self.screen.blit(deck_txt, (10, SCREEN_H - 20))
    
    def _draw_slot_ui(self):
        """UI für Slot-Phase"""
        # Eingehender Schaden auch hier sichtbar (Block-Planung)
        self.ui.draw_player_hp_preview(self.player, 0, self._incoming_damage())
        # Phase-Anzeige
        phase_txt = self.ui.font_title.render("🎰 SLOT-PHASE", True, GOLD)
        self.screen.blit(phase_txt, (SCREEN_W//2 - phase_txt.get_width()//2, 490))
        
        spin_y = 680
        if self.spins_remaining > 0 and not self.slot_machine.spinning:
            self.ui.draw_button(
                f"🎰 DREHEN! ({self.spins_remaining}x)",
                SCREEN_W//2 - 80, spin_y, 160, 45,
                color=GOLD, pulsing=True
            )
        elif self.slot_machine.spinning:
            self.ui.draw_button("⚡ Dreht...", SCREEN_W//2 - 80, spin_y, 160, 45,
                               color=GREY_DARK, disabled=True)
        
        if self.spins_remaining == 0 and not self.slot_machine.spinning:
            if self.slot_death_pending:
                # Gegner tot durch Slot – kurz warten, dann Belohnung
                win_txt = self.ui.font_title.render("🏆 GEGNER BESIEGT!", True, GOLD)
                self.screen.blit(win_txt, (SCREEN_W//2 - win_txt.get_width()//2, 735))
            else:
                if not self.slot_done:
                    # 0 Spins (z.B. durch Slot-Jam) -> Hinweis statt leerer Phase
                    hint = self.ui.font_small.render("🎰 Automat blockiert – keine Drehung!",
                                                     True, ORANGE)
                    self.screen.blit(hint, (SCREEN_W//2 - hint.get_width()//2, 700))
                self.ui.draw_button("➡️ Weiter", SCREEN_W//2 - 80, 735, 160, 40,
                                   color=GREEN, pulsing=True)
    
    def _draw_slot_effects(self):
        """Zeigt Slot-Effekte als modernes Panel"""
        shown = self.slot_effects_shown[:8]
        eff_x, eff_y = 808, 84
        eff_w = 376
        eff_h = 30 + len(shown) * 22 + 6
        self.ui._panel((eff_x, eff_y, eff_w, eff_h), radius=12, border=GOLD_DARK)
        self.ui._text("🎰 SLOT-ERGEBNISSE", self.ui.font_small, ACCENT, eff_x + 12, eff_y + 8)
        pygame.draw.line(self.screen, (*GOLD_DARK, 150),
                         (eff_x + 10, eff_y + 28), (eff_x + eff_w - 10, eff_y + 28))
        for i, eff in enumerate(shown):
            self.ui._text(eff[:50], self.ui.font_tiny, CYAN, eff_x + 12, eff_y + 34 + i * 22)
    
    def _draw_enemy_turn_ui(self):
        """UI während Gegner-Zug"""
        txt = self.ui.font_title.render("💀 FEIND AM ZUG...", True, RED)
        self.screen.blit(txt, (SCREEN_W//2 - txt.get_width()//2, 490))
        
        # Countdown-Bar
        bar_w = 300
        prog = max(0, self.enemy_turn_timer / 1.5)
        pygame.draw.rect(self.screen, GREY_DARK,
                         (SCREEN_W//2 - bar_w//2, 525, bar_w, 12), border_radius=4)
        pygame.draw.rect(self.screen, RED,
                         (SCREEN_W//2 - bar_w//2, 525, int(bar_w * prog), 12), border_radius=4)
    
    def _draw_reward(self):
        """Belohnungsbildschirm"""
        self.reward_card_rects, self.reward_skip_rect = self.ui.draw_reward_screen(
            self.reward_cards, self.gold_reward, self.player, relic=self.reward_relic
        )

    def _draw_event(self):
        """Event-Bildschirm"""
        self.event_option_rects, self.event_continue_rect = self.ui.draw_event(
            self.current_event, self.event_resolved, self.event_result,
            self.hovered_event_idx
        )

    def _draw_shop(self):
        """Shop-Bildschirm (Overlays werden global gezeichnet)"""
        (self.shop_item_rects, self.shop_gamble_rect,
         self.shop_leave_rect) = self.ui.draw_shop(
            self.shop_items, self.player, self.shop_message, self.shop_purchased)

    def _draw_scores(self):
        """Highscore-Bildschirm"""
        self.scores_back_rect = self.ui.draw_scores(self.highscores)
