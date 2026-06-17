"""Haupt-Spielklasse: State Machine für alle Spielphasen"""

import pygame
import random
import math
from constants import *
from entities import Player, Enemy, Card
from slots import SlotMachine
from ui import UIRenderer
from card_effects import CardEffectResolver
from highscores import load_highscores, add_highscore
import savegame
import audio
import mapgen
import options
import slotmode
import assets
import achievements
import daily
import stats
import updater


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
STATE_ACT_CLEAR   = "act_clear"      # "Akt geschafft"-Bildschirm (Boss besiegt)
STATE_COMBAT      = "combat"
STATE_PLAYER_TURN = "player_turn"    # Karten spielen
STATE_SLOT_SPIN   = "slot_spin"      # Slot dreht sich
STATE_ENEMY_TURN  = "enemy_turn"     # Gegner agiert
STATE_REWARD      = "reward"         # Belohnungsbildschirm
STATE_RELIC_REWARD = "relic_reward"  # Relikt-Auswahl (3 zur Wahl)
STATE_EVENT       = "event"          # Zufalls-Event zwischen Etagen
STATE_SHOP        = "shop"           # Laden zwischen Etagen
STATE_GAME_OVER   = "game_over"
STATE_VICTORY     = "victory"
STATE_SCORES      = "scores"         # Highscore-Anzeige
STATE_ACHIEVEMENTS = "achievements"  # Erfolge-Anzeige
STATE_CLASS_SELECT = "class_select"  # Klassenauswahl vor dem Run
STATE_SLOTMODE     = "slotmode"      # Reiner Slot-Modus (eigenes Spiel)


# ═══════════════════════════════════════════════
# AKT-THEMEN  (zyklisch ab Akt 1; gibt jedem Akt eine eigene Gegner-Auswahl,
# Namen, Tönung und Hintergrund). Tuple: (name, accent_rgb, bg, [gegner], boss)
# ═══════════════════════════════════════════════
ACT_THEMES = [
    ("Die Kneipe", (210, 150, 60), "bg_kneipe", [
        "Schluffiger Goblin", "Betrunkener Ritter", "Pestratte",
        "Steuerprüfer", "Kneipenschläger", "Sumpfschleim", "Wütender Koch",
        "Würfelgnom", "Bierbauch-Ork",
    ], "DER GROSSE HÜHNERKÖNIG"),
    ("Das Untergrund-Casino", (210, 80, 150), "bg_casino", [
        "Vampir-Croupier", "Slot-Maschinendämon", "Glücksgeist",
        "Steuerprüfer", "Kneipenschläger", "Falschspieler", "Einarmiger Bandit",
        "Roulette-Geist", "Münzgolem",
    ], ["Oberster Glücksprüfer", "DER BANKHALTER"]),
    ("Das Verfluchte Reich", (150, 90, 220), "bg_cursed", [
        "Philosophischer Lich", "Verfluchter Spiegel", "Pilzkönigin",
        "Wütender Koch", "Pestratte", "Glücksgeist", "Sumpfschleim",
        "Geisterbraut", "Knochenkoch", "Schattenkrähe", "Gruftwächter",
    ], ["MADAME FORTUNA", "DER SENSENMANN"]),
    ("Die Kanalisation", (90, 150, 70), "bg_sewer", [
        "Riesenkanalratte", "Seuchendoktor", "Sumpfschleim", "Pestratte",
        "Knochenkoch", "Gruftwächter",
    ], "DIE BRUTMUTTER"),
    ("Der Frostpalast", (120, 200, 230), "bg_frost", [
        "Frostgolem", "Eishexe", "Gruftwächter", "Slot-Maschinendämon",
        "Münzgolem", "Schattenkrähe",
    ], "DER FROSTKÖNIG"),
    ("Die Unterwelt", (220, 70, 50), "bg_hell", [
        "Höllenhund", "Qualdämon", "Wütender Koch", "Vampir-Croupier",
        "Schattenkrähe", "Gruftwächter",
    ], ["LUZIFER", "DER SENSENMANN"]),
    # ─── v1.16: neue Akte 7–11 ───
    ("Der Geister-Saloon", (210, 180, 120), "bg_saloon", [
        "Revolver-Skelett", "Pokergeist", "Whiskey-Schemen",
        "Schattenkrähe", "Roulette-Geist",
    ], "DOC KNOCHENHAND"),
    ("Die Spiegelhalle", (180, 185, 225), "bg_mirror", [
        "Spiegelscherbe", "Trugbild", "Zerrbild",
        "Verfluchter Spiegel", "Geisterbraut",
    ], "DEIN SPIEGEL-ICH"),
    ("Der Hochroller-Salon", (230, 195, 80), "bg_vip", [
        "Goldwächter", "VIP-Dämon", "Salon-Croupier",
        "Münzgolem", "Vampir-Croupier",
    ], "DER HAUSHERR"),
    ("Der Maschinenraum", (200, 160, 90), "bg_machine", [
        "Zahnrad-Golem", "Wartungs-Automat", "Dampf-Schläger",
        "Münzgolem", "Slot-Maschinendämon",
    ], "DER JACKPOT-AUTOMAT"),
    ("Die Leere", (140, 110, 210), "bg_void", [
        "Leeren-Wandler", "Sternenfresser", "Echo des Nichts",
        "Schattenkrähe", "Gruftwächter",
    ], ["DER CROUPIER DES NICHTS", "DER SENSENMANN"]),
]


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
        # Slot-Modus (eigenes Spiel)
        self.slotrun = None
        self._sm_spinning = False
        self._sm_pending = []
        self._sm_by_name = {s["name"]: s for s in SLOT_SYMBOLS}
        
        # UI-Zustände
        self.selected_card = None
        self.hovered_card_idx = None
        self.card_rects = []
        self.reward_cards = []
        self.gold_reward = 0
        self.reward_card_rects = []
        self.reward_skip_rect = None
        self.reward_relic = None      # Relikt-Belohnung (Elite/Boss)
        self.relic_choices = []       # 3 Relikte zur Auswahl (Elite/Boss)
        self.relic_choice_rects = []
        self.hovered_relic_idx = None

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
        # Scroll im Karten-Raster (Aufwerten/Verbrennen), in Reihen
        self.grid_scroll = 0

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
        self.shop_gamble_count = 0     # Anzahl Glücksrad-Drehungen im aktuellen Shop
        
        # Tages-Challenge-Zustand
        self.daily_mode = False
        self.daily_mod = None
        self.daily_result = None
        self.lifetime_stats = stats.load()

        # Klassenauswahl-Zustand
        self.pending_daily = False
        self.class_select_rects = []
        self.class_back_rect = None

        # In-Game-Updater: alte EXE aufräumen + Versions-Check im Hintergrund
        updater.cleanup_old()
        updater.check_async(GAME_VERSION)
        self.update_btn_rect = None

        # Erfolge: laden + Toast-Warteschlange [(def, restzeit), ...]
        achievements.load()
        self.achievement_toasts = []
        self.achievements_back_rect = None

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
        self._cleared_act = 1       # zuletzt abgeschlossener Akt (für Akt-Geschafft-Screen)
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
        # SCALED: pygame rendert intern auf SCREEN_W×SCREEN_H und skaliert
        # auf die tatsächliche Fenstergröße – so passen alle Bildschirmgrößen.
        if self.options.get("fullscreen"):
            flags = pygame.SCALED | pygame.FULLSCREEN
        else:
            flags = pygame.SCALED   # Fenstermodus: skaliert trotzdem korrekt
        try:
            self.display = pygame.display.set_mode((SCREEN_W, SCREEN_H), flags)
        except Exception:
            self.options["fullscreen"] = False
            try:
                self.display = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.SCALED)
            except Exception:
                self.display = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        # Fenster-Icon (neu setzen, da set_mode es zurücksetzen kann)
        try:
            ic = assets.load("ui", "icon_256")
            if ic:
                pygame.display.set_icon(ic)
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
                else:
                    self._handle_key(event.key)

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
                  STATE_SHOP, STATE_EVENT, STATE_REWARD, STATE_RELIC_REWARD,
                  STATE_MAP, STATE_REST, STATE_ACT_CLEAR)

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
                            STATE_ACHIEVEMENTS, STATE_CLASS_SELECT,
                            STATE_GAME_OVER, STATE_VICTORY, STATE_SLOTMODE):
            self.state = STATE_MENU
        else:  # Hauptmenü
            self.running = False

    def _handle_key(self, key):
        """Tastatursteuerung: Karten 1-9, Leertaste = drehen / Zug beenden / weiter."""
        # Zahlentasten 1..9
        if pygame.K_1 <= key <= pygame.K_9:
            idx = key - pygame.K_1
            if self.state == STATE_PLAYER_TURN:
                if idx < len(self.player.hand or []):
                    self._try_play_card(self.player.hand[idx])
            elif self.state == STATE_REWARD and self.reward_card_rects:
                if idx < len(self.reward_card_rects):
                    self._pick_reward_card(idx)
            elif self.state == STATE_RELIC_REWARD:
                if idx < len(self.relic_choices):
                    audio.play("click")
                    self._pick_relic_reward(idx)
            return

        if key in (pygame.K_SPACE, pygame.K_RETURN):
            if self.state == STATE_PLAYER_TURN:
                self._start_slot_phase()                 # = "Slot drehen"
            elif self.state == STATE_SLOT_SPIN:
                can_spin = (self.spins_remaining > 0 and not self.slot_machine.spinning
                            and not self.slot_death_pending
                            and self.enemy is not None and self.enemy.hp > 0)
                if can_spin:
                    self._do_spin()
                elif (self.spins_remaining == 0 and not self.slot_machine.spinning
                      and not self.slot_death_pending):
                    self._start_enemy_turn()             # = "Weiter"
            elif self.state == STATE_REWARD:
                self._skip_reward()                      # = "Überspringen"
            elif self.state == STATE_ACT_CLEAR:
                audio.play("click"); self.state = STATE_MAP
            elif self.state == STATE_SLOTMODE and self.slotrun:
                r = self.slotrun
                if r.in_shop:
                    audio.click(); r.next_round()
                elif not r.game_over and not self._sm_spinning:
                    self._sm_spin()

    def _compute_menu_layout(self):
        """Layout der Hauptmenü-Buttons. Quelle für Zeichnen UND Klick."""
        cx = SCREEN_W // 2
        changelog = pygame.Rect(16, SCREEN_H - 50, 200, 34)
        if savegame.has_valid_save():
            return {
                "resume":   pygame.Rect(cx - 130, 406, 260, 46),
                "play":     pygame.Rect(cx - 130, 458, 260, 40),
                "daily":    pygame.Rect(cx - 130, 502, 260, 38),
                "slotmode": pygame.Rect(cx - 130, 544, 260, 38),
                "tutorial": pygame.Rect(cx - 110, 586, 220, 34),
                "options":  pygame.Rect(cx - 110, 624, 220, 34),
                "scores":   pygame.Rect(cx - 110, 662, 220, 34),
                "achievements": pygame.Rect(cx - 110, 700, 220, 34),
                "changelog": changelog,
            }
        return {
            "resume":   None,
            "play":     pygame.Rect(cx - 110, 430, 220, 48),
            "daily":    pygame.Rect(cx - 110, 482, 220, 40),
            "slotmode": pygame.Rect(cx - 110, 526, 220, 40),
            "tutorial": pygame.Rect(cx - 110, 570, 220, 38),
            "options":  pygame.Rect(cx - 110, 612, 220, 38),
            "scores":   pygame.Rect(cx - 110, 654, 220, 38),
            "achievements": pygame.Rect(cx - 110, 696, 220, 38),
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
            "fullscreen": pygame.Rect(px + 488, 400, 72, 32),
            "shake":      pygame.Rect(px + 488, 444, 72, 32),
            "particles":  pygame.Rect(px + 488, 488, 72, 32),
            "fast":       pygame.Rect(px + 488, 532, 72, 32),
        }
        # Schwierigkeits-Auswahl: drei Segment-Buttons
        diff = [pygame.Rect(px + 250 + i * 110, 578, 100, 34) for i in range(3)]
        return {
            "panel": pygame.Rect(px, 150, 600, 540),
            "sliders": sliders,
            "toggles": toggles,
            "difficulty": diff,
            "back":     pygame.Rect(cx - 200, 632, 180, 44),
            "defaults": pygame.Rect(cx + 20, 632, 180, 44),
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
        for i, dr in enumerate(lay.get("difficulty", [])):
            if dr.collidepoint(pos):
                self.options["difficulty"] = i
                audio.click(); options.save(self.options)
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
        elif self.state == STATE_RELIC_REWARD:
            self.hovered_relic_idx = None
            for i, rect in enumerate(self.relic_choice_rects):
                if rect and rect.collidepoint(pos):
                    self.hovered_relic_idx = i
                    break
        elif self.state == STATE_MAP:
            self.hovered_node = None
            for n in self._map_available():
                if (pos[0] - n["x"]) ** 2 + (pos[1] - n["y"]) ** 2 <= (mapgen.NODE_R + 6) ** 2:
                    self.hovered_node = [n["row"], n["col"]]
                    break

    def _handle_scroll(self, delta_y):
        """Mausrad-Scrolling: Karten-Raster (Overlay) vor Kampflog"""
        # Karten-Raster (Aufwerten/Verbrennen): bei großen Decks scrollen
        if self.shop_remove_mode or self.shop_upgrade_mode:
            total = len(self.player.deck + self.player.discard + self.player.hand)
            rows = (total + 7) // 8                  # 8 Karten pro Reihe
            max_scroll = max(0, rows - 3)            # 3 Reihen passen auf den Schirm
            self.grid_scroll = max(0, min(max_scroll, self.grid_scroll - delta_y))
            return

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

        if self.state == STATE_SLOTMODE:
            self._handle_slotmode_click(pos)
            return

        if self.state == STATE_MENU:
            # Update-Button (nur wenn neuere Version verfügbar)
            if self.update_btn_rect and self.update_btn_rect.collidepoint(pos):
                audio.play("click"); updater.apply_update()
                return
            lay = self._compute_menu_layout()
            if lay["resume"] and lay["resume"].collidepoint(pos):
                audio.play("click"); self._load_run()
                return
            if lay["play"].collidepoint(pos):
                audio.play("click"); self.pending_daily = False
                self.state = STATE_CLASS_SELECT
                return
            if lay["daily"].collidepoint(pos):
                audio.play("click"); self.pending_daily = True
                self.state = STATE_CLASS_SELECT
                return
            if lay.get("slotmode") and lay["slotmode"].collidepoint(pos):
                audio.play("click"); self._start_slotmode()
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
            if lay["achievements"].collidepoint(pos):
                audio.play("click"); self.state = STATE_ACHIEVEMENTS
                return
            if lay["changelog"].collidepoint(pos):
                audio.play("click"); self.state = STATE_CHANGELOG
                return

        elif self.state == STATE_CHANGELOG:
            back = pygame.Rect(SCREEN_W//2 - 100, SCREEN_H - 62, 200, 44)
            if back.collidepoint(pos):
                audio.play("click"); self.state = STATE_MENU
            return

        elif self.state == STATE_ACT_CLEAR:
            cont = pygame.Rect(SCREEN_W//2 - 110, SCREEN_H - 110, 220, 50)
            if cont.collidepoint(pos):
                audio.play("click"); self.state = STATE_MAP
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
            
            # "Slot drehen"-Button (= Runde beenden) – mittig über dem Log
            end_btn = pygame.Rect(SCREEN_W//2 - 105, 240, 210, 48)
            if end_btn.collidepoint(pos):
                self._start_slot_phase()
                return
            
            # Karte abwählen
            self.selected_card = None
        
        elif self.state == STATE_SLOT_SPIN:
            # Spin-Button (nicht, wenn Gegner schon tot ist -> Sieg läuft)
            if (self.spins_remaining > 0 and not self.slot_machine.spinning
                    and not self.slot_death_pending
                    and self.enemy is not None and self.enemy.hp > 0):
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
        
        elif self.state == STATE_RELIC_REWARD:
            for i, rect in enumerate(self.relic_choice_rects):
                if rect and rect.collidepoint(pos):
                    audio.play("click")
                    self._pick_relic_reward(i)
                    return

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

        elif self.state == STATE_ACHIEVEMENTS:
            if self.achievements_back_rect and self.achievements_back_rect.collidepoint(pos):
                audio.play("click"); self.state = STATE_MENU

        elif self.state == STATE_CLASS_SELECT:
            for i, rect in enumerate(self.class_select_rects or []):
                if rect and rect.collidepoint(pos):
                    audio.play("click")
                    self._start_game(daily_mode=self.pending_daily,
                                     class_def=CLASS_DEFINITIONS[i])
                    return
            if self.class_back_rect and self.class_back_rect.collidepoint(pos):
                audio.play("click"); self.state = STATE_MENU
        
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

        # Items neu mischen (Reroll)
        if getattr(self, "shop_reroll_rect", None) and self.shop_reroll_rect.collidepoint(pos):
            self._reroll_shop()
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
            self.grid_scroll = 0
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
    
    def _start_game(self, daily_mode=False, class_def=None):
        savegame.delete_save()   # Neuer Run verwirft alten Speicherstand
        self.daily_mode = daily_mode
        self.daily_mod = daily.modifier_for_today() if daily_mode else None
        if daily_mode:
            # Fester Tages-Seed: alle Spieler bekommen heute dieselbe Karte
            random.seed(daily.seed_for_today())
        self.player = Player(class_def)
        # Start-Relikt der Klasse vergeben
        if class_def and class_def.get("relic"):
            rdef = next((r for r in RELIC_DEFINITIONS if r["id"] == class_def["relic"]), None)
            if rdef:
                self.player.add_relic(rdef)
        self.floor_num = 1
        self.turn_num = 1
        self.act = 1
        self.combat_log = []
        self.score_saved = False
        self.last_score = 0
        self.last_rank = None
        self.last_is_record = False
        self.daily_result = None   # (new_best, streak) nach Tages-Run
        self.gamemap = mapgen.generate(self.act)
        self.map_current = None
        self.current_node = None

        # Tages-Modifikator auf den Spieler anwenden
        m = self.daily_mod or {}
        if "max_hp" in m:
            self.player.max_hp = m["max_hp"]; self.player.hp = m["max_hp"]
        if "bonus_energy" in m:
            self.player.max_energy += m["bonus_energy"]
        if "start_gold" in m:
            self.player.gold = m["start_gold"]
        if "start_strength" in m:
            self.player.perm_strength += m["start_strength"]
        if "heal_mult" in m:
            self.player.heal_mult = m["heal_mult"]

        self.state = STATE_MAP
    
    def _act_theme(self):
        """Akt-Thema (name, accent, gegner-namen, boss-name) – zyklisch."""
        return ACT_THEMES[(self.act - 1) % len(ACT_THEMES)]

    def _spawn_enemy(self, node_type="combat"):
        """Wählt einen Gegner aus dem Pool des aktuellen Akts, passend zur Tiefe."""
        import copy
        is_elite = (node_type == "elite")
        _name, _accent, _bg, pool_names, boss_name = self._act_theme()
        by_name = {e["name"]: e for e in ENEMY_TYPES}
        pool = [by_name[n] for n in pool_names if n in by_name]
        # erste Etagen im Akt: nur Tier-1-Gegner aus dem Pool (Einstieg fairer)
        row_in_act = (self.floor_num - 1) % mapgen.ROWS

        if node_type == "boss":
            choices = boss_name if isinstance(boss_name, list) else [boss_name]
            pick = random.choice(choices)
            enemy_def = by_name.get(pick)
            if enemy_def is None:
                enemy_def = random.choice([e for e in ENEMY_TYPES if e.get("is_boss")])
        else:
            cands = [e for e in pool if not e.get("is_boss")]
            if not is_elite and row_in_act <= 1:
                tier1 = [e for e in cands if e.get("tier", 1) == 1]
                cands = tier1 or cands
            if not cands:  # Sicherheitsnetz
                cands = [e for e in ENEMY_TYPES if e.get("tier", 1) <= 2 and not e.get("is_boss")]
            enemy_def = random.choice(cands)

        # Gegner skaliert mit der Tiefe (über Akte hinweg).
        enemy_def = copy.deepcopy(enemy_def)
        f = self.floor_num
        # HP skaliert STEILER als der Schaden: lange Kämpfe statt 1-Shots.
        # Zusätzlich ein leicht überlinearer Term, damit Spät-Etagen nicht
        # vom Stärke-Schneeball trivialisiert werden.
        hp_per = 0.10 if node_type == "boss" else 0.17
        hp_scale = 1.0 + (f - 1) * hp_per + ((f - 1) ** 2) * 0.0025
        dmg_per = 0.06 if node_type == "boss" else 0.10
        dmg_scale = 1.0 + (f - 1) * dmg_per
        enemy_def["hp"] = int(enemy_def["hp"] * hp_scale)
        enemy_def["max_hp"] = enemy_def["hp"]
        enemy_def["damage"] = int(enemy_def["damage"] * dmg_scale)
        # Skalierende RÜSTUNG (flache Reduktion pro Treffer) – bremst reines
        # Stärke-Stacking & Multi-Hit-Karten, je tiefer desto mehr.
        armor_bonus = f // 8 + (3 if node_type == "boss" else 0)
        enemy_def["armor"] = enemy_def.get("armor", 0) + armor_bonus

        # Schwierigkeitsgrad (Optionen): skaliert Gegner-HP/-Schaden
        try:
            _dname, hp_mul, dmg_mul = options.DIFFICULTY[self.options.get("difficulty", 1)]
            enemy_def["hp"] = max(1, int(enemy_def["hp"] * hp_mul))
            enemy_def["max_hp"] = enemy_def["hp"]
            enemy_def["damage"] = max(1, int(enemy_def["damage"] * dmg_mul))
        except (IndexError, KeyError, TypeError):
            pass

        # Tages-Modifikatoren (Gegner-Seite)
        m = self.daily_mod or {}
        if m.get("enemy_hp_mult"):
            enemy_def["hp"] = int(enemy_def["hp"] * m["enemy_hp_mult"])
            enemy_def["max_hp"] = enemy_def["hp"]
        if m.get("enemy_dmg_mult"):
            enemy_def["damage"] = int(enemy_def["damage"] * m["enemy_dmg_mult"])

        if is_elite:
            enemy_def["name"] = "⭐ Elite-" + enemy_def["name"]
            enemy_def["hp"] = int(enemy_def["hp"] * 1.4)
            enemy_def["max_hp"] = enemy_def["hp"]
            enemy_def["damage"] = int(enemy_def["damage"] * 1.25)
            enemy_def["armor"] = enemy_def.get("armor", 0) + 2
            enemy_def["is_elite"] = True

        self.enemy = Enemy(enemy_def)
        if (self.daily_mod or {}).get("enemy_start_poison"):
            self.enemy.poison = self.daily_mod["enemy_start_poison"]

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
                self._begin_act_clear()
                self._autosave()
                return
        self.state = STATE_MAP
        self._autosave()   # Autosave zwischen den Knoten

    def _begin_act_clear(self):
        """Boss besiegt -> 'Akt geschafft'-Bildschirm, nächster Akt schon vorbereitet."""
        self._cleared_act = self.act
        if self._cleared_act >= 1:
            self._award("act1")
        if self._cleared_act >= 3:
            self._award("act3")
            cid = getattr(self.player, "class_id", None)
            self._award({"knight": "win_knight", "gambler": "win_gambler",
                         "witch": "win_witch"}.get(cid, ""))
        # Nächsten (härteren) Akt schon generieren, damit Speichern/Weiter sauber ist
        self.act += 1
        self.gamemap = mapgen.generate(self.act)
        self.map_current = None
        self.current_node = None
        self.map_message = f"🏔️ AKT {self.act} – es wird härter!"
        self.map_message_timer = 3.0
        audio.stop_spin()
        audio.play("fanfare")
        self.state = STATE_ACT_CLEAR
    
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
        # Kampf-gebundene Status laufen zwischen Kämpfen ab
        self.player.poison = 0
        self.player.regen = 0
        self.player.thorns = 0
        self.player.dodge = False
        # Stärke ist jetzt PRO KAMPF: zu Kampfbeginn auf die permanente
        # Basis zurücksetzen (kein Stärke-Schneeball über Kämpfe hinweg).
        self.player.strength = getattr(self.player, "perm_strength", 0)
        self.player.rage = 0
        self.player.focus = 0
        self.player.vulnerable = 0
        self.player.mult = 1.0          # Multiplikator pro Kampf zurücksetzen
        self.player.war_dance = 0
        self._combat_first_spin = True  # Walzen-Joker: erster Dreh dieses Kampfes
        self.player.next_spin_lucky = False
        self.player.next_spin_wild = False
        self.player.next_spin_double = False
        self.player.next_spin_triple = False
        self.player.next_free_card = self.player.has_relic("first_free")
        self.player.draw_initial_hand()
        self.damage_numbers = []
        self.slot_effects_shown = []
        self._log(f"--- Etage {self.floor_num}: {self.enemy.name} erscheint! ---")
        self._log(f"{self.enemy.tooltip}")

        # ─── Relik-Effekte zu Kampfbeginn ───
        self._apply_combat_start_relics()
        # ─── Klassenbuff (Kampfbeginn) ───
        self._first_card_used = False
        if self._class_buff() == "house_edge":
            self.player.lucky += 1
            self._log("🃏 Hausvorteil: +1 Glücksrunde!")
        self._apply_class_turn_buff()

    def _class_buff(self):
        """Aktiver Klassenbuff (id) oder None."""
        cd = getattr(self.player, "class_def", None)
        return cd.get("buff") if cd else None

    def _apply_class_turn_buff(self):
        """Klassen-Passive zu jedem Rundenstart."""
        buff = self._class_buff()
        e = self.enemy
        if buff == "guardian":
            self.player.block += 3
        elif buff == "hexweave" and e:
            # Flüche fressen sich tiefer: +1 auf vorhandene Debuffs am Gegner
            grew = False
            for attr in ("poison", "burn", "frost"):
                if getattr(e, attr, 0) > 0:
                    setattr(e, attr, getattr(e, attr) + 1); grew = True
            if grew:
                self._log("🕸️ Fluchweberin: deine Flüche fressen sich tiefer (+1)!")
        elif buff == "alchemy" and e and e.poison > 0:
            e.poison += 2
            self._log("⚗️ Giftmischer: +2 Gift auf den Gegner!")

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
        # Wachturm: +6 Block zu Beginn jeder Runde
        if self.player.has_relic("watchtower"):
            self.player.block += 6
        # Doppeldecker: +1 Karte pro Runde
        if self.player.has_relic("extra_draw"):
            self.player.draw_hand(1)
        # Fokuslinse: +2 Fokus pro Runde
        if self.player.has_relic("focus_lens"):
            self.player.focus += 2
        # Falsches Ass: erste Karte der Runde gratis
        if self.player.has_relic("first_free"):
            self.player.next_free_card = True
        # ─── Klassenbuffs (Rundenstart) ───
        self._first_card_used = False
        self._quick_used = False
        if self.player.has_relic("dice_luck"):
            self.player.lucky += 1
        self._apply_class_turn_buff()
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
        # Kettenhemd / Phönixfeder pro Kampf scharf schalten
        p.flat_reduction = 2 if p.has_relic("chainmail") else 0
        p.has_phoenix = p.has_relic("phoenix")
        if p.has_relic("start_block"):
            p.block += 12
            self._log("🛡️ Eiserner Wille: +12 Block!")
        if p.has_relic("purse"):
            p.add_gold(8)
            self._log("💰 Dukatenbeutel: +8 Gold!")
        if p.has_relic("mirror_shield"):
            p.reflect = True
            self._log("🪞 Spiegelschild: Reflektor aktiv!")
        if p.has_relic("interest"):
            bonus = min(10, p.gold // 25)
            if bonus > 0:
                p.add_gold(bonus)
                self._log(f"💰 Spardose: +{bonus} Gold Zinsen!")
        if p.has_relic("chicken_relic") and random.random() < 0.4:
            log = self.slot_machine._chicken_effect(p, self.enemy) if self.slot_machine else None
            self._log(f"🐔 Hühner-Totem: {log}" if log else "🐔 Hühner-Totem: Ein Huhn erscheint!")
        if p.has_relic("fortune_cookie"):
            p.lucky += 1
            self._log("🥠 Glückskeks: +1 Glücksrunde!")
        if p.has_relic("four_leaf"):
            p.bonus_spins += 1
            p.lucky += 1
            self._log("🍀 Vierblättriger Klee: +1 Dreh, +1 Glücksrunde!")
        if p.has_relic("witch_cauldron") and self.enemy:
            self.enemy.poison += 3
            self._log("🧪 Hexenkessel: Gegner startet mit 3 Gift!")
        # ─── Neue Relikte (v1.12.0) ───
        e = self.enemy
        if p.has_relic("frostbite") and e:
            e.frost += 2; self._log("❄️ Eiszapfen-Amulett: Gegner +2 Frost!")
        if p.has_relic("branding") and e:
            e.marked += 3; self._log("🔥 Brandeisen: Gegner +3 markiert!")
        if p.has_relic("thorn_crown"):
            p.thorns += 4; self._log("👑 Dornenkrone: +4 Dornen!")
        if p.has_relic("rage_totem"):
            p.rage += 1; self._log("😤 Wuttotem: +1 Wut!")
        if p.has_relic("berserker_blood") and p.hp < p.max_hp // 2:
            p.strength += 3; self._log("🩸 Berserkerblut: +3 Stärke (unter 50% HP)!")
        if p.has_relic("ice_heart"):
            p.dodge = True; self._log("🧊 Eisherz: du weichst dem ersten Treffer aus!")
        if p.has_relic("doom_bell") and e and random.random() < 0.35:
            e.doom = 4; self._log("🔔 Schicksalsglocke: VERHÄNGNIS über den Gegner!")
        if p.has_relic("time_glass"):
            p.energy += 1; self._log("⏳ Zeitsanduhr: +1 Energie (erste Runde)!")
        if p.has_relic("card_master"):
            drawn = p.draw_hand(2); self._log(f"🎴 Kartenmeister: +{drawn} Karten!")
        if p.has_relic("focus_lens"):
            p.focus += 2; self._log("🔎 Fokuslinse: +2 Fokus!")
        # ─── v1.17: Build-Anker zu Kampfbeginn ───
        if p.has_relic("spike_armor"):
            p.thorns += 4; self._log("🦔 Stachelpanzer: +4 Dornen!")
        if p.has_relic("luck_amulet"):
            p.lucky += 2; self._log("🍀 Glücksamulett: +2 Glücksrunden!")
        if p.has_relic("arsonist") and e:
            e.burn += 3; self._log("🪔 Brandstifter: Gegner startet mit 3 Brennen!")
        if p.has_relic("mult_core"):
            p.mult = max(p.mult, 1.5); self._log("✖️ Multiplikator-Kern: Mult startet bei 1.5!")
        if p.has_relic("gold_reserve"):
            gb = p.gold // 50
            if gb > 0:
                p.strength += gb; self._log(f"🏆 Goldreserve: +{gb} Stärke (aus Reichtum)!")
        self._combat_card_count = 0          # für Giftphiole/Berserkermal/Schnelldenker
        if (self.daily_mod or {}).get("start_lucky"):
            p.lucky += self.daily_mod["start_lucky"]
            self._log(f"📅 Glückstag: +{self.daily_mod['start_lucky']} Glücksrunde!")

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

        self.player.best_combo = max(self.player.best_combo, self.combo_count)
        if self.combo_count >= 2:
            if self.combo_count >= 5:
                self._award("combo_5")
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
        # Hochstapler 'Falschspieler': erste Karte pro Runde kostet 1 weniger
        if (not free and not getattr(self, "_first_card_used", True)
                and self._class_buff() == "cardsharp"):
            cost = max(0, cost - 1)
        if cost > self.player.energy:
            self._log(f"❌ Nicht genug Energie für '{card.name}'! ({card.cost} nötig)")
            audio.play("error", 0.6)
            return
        if free:
            self.player.next_free_card = False
            self._log(f"✨ '{card.name}' gratis gespielt!")

        audio.play("card", 0.7)
        self.player.energy -= cost
        self._first_card_used = True   # Falschspieler-Rabatt verbraucht
        self.player.hand.remove(card)
        # Exhaust-Karten verschwinden für immer (nicht in den Abwurfstapel)
        if not card.exhaust:
            self.player.discard.append(card)

        # Snapshots für Effekt-Feedback
        e_hp0 = self.enemy.hp
        p_hp0 = self.player.hp
        blk0 = self.player.block
        gold0 = self.player.gold

        # ─── v1.17: Relikt-Hooks beim Kartenspielen ───
        self._combat_card_count = getattr(self, "_combat_card_count", 0) + 1
        if self.player.has_relic("poison_vial_relic") and self._combat_card_count % 3 == 0 and self.enemy:
            self.enemy.poison += 1
            self._log("🧫 Giftphiole: +1 Gift!")
        if card.type == "attack" and self.player.has_relic("berserk_mark"):
            self.player.strength += 1
        if (cost == 0 and self.player.has_relic("quick_thinker")
                and not getattr(self, "_quick_used", False)):
            self._quick_used = True
            drawn = self.player.draw_hand(1)
            if drawn:
                self._log("⚡ Schnelldenker: Karte nachgezogen!")

        # Kriegstanz: jede Angriffskarte diese Runde gibt +Stärke (bleibt im Kampf)
        if card.type == "attack" and getattr(self.player, "war_dance", 0) > 0:
            self.player.strength += self.player.war_dance
            self._log(f"⚔️ Kriegstanz: +{self.player.war_dance} Stärke!")

        # Fokus: nächste Angriffskarte bekommt +Fokus Schaden (über Stärke), einmalig
        focus_applied = 0
        if card.type == "attack" and self.player.focus > 0:
            focus_applied = self.player.focus
            self.player.strength += focus_applied
            self.player.focus = 0

        logs = self.resolver.resolve(card, self.player, self.enemy, self.slot_machine)
        for log in logs:
            self._log(log)
        if focus_applied:
            self.player.strength -= focus_applied
            self._log(f"🎯 Fokus verbraucht (+{focus_applied} Schaden)")

        # Aderlass-Amulett: Heilung beim Spielen von Angriffskarten
        if card.type == "attack" and self.player.has_relic("leech_charm"):
            healed = self.player.heal_hp(2)
            if healed > 0:
                self._log(f"🧛 Aderlass-Amulett: +{healed} HP")

        if card.exhaust:
            self._log("   ♻️ Karte verbraucht und entfernt.")

        # Combo-System
        for log in self._bump_combo(card):
            self._log(log)

        # Münzregen: Gold pro gespielter Karte
        if self.player.coin_rain_active:
            self.player.add_gold(10)
            self._log("   🪙 Münzregen: +10 Gold!")
        # Glücksmünze-Relikt: +1 Gold pro Karte
        if self.player.has_relic("lucky_coin"):
            self.player.add_gold(1)

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
        # Gegner schon tot (z.B. erster von mehreren Spins) -> nicht weiterdrehen,
        # sonst läuft der Dreh-Sound endlos und man landet doppelt im Sieg.
        if self.slot_death_pending or self.enemy is None or self.enemy.hp <= 0:
            return

        self.spins_remaining -= 1
        self.player.slots_spun += 1
        # Trinkgeld-Relikt: Gold pro Dreh
        if self.player.has_relic("tip_jar"):
            self.player.add_gold(2)
        # Gezinkte Würfel/Karte: Glück. Sonst Glücksrunden verbrauchen.
        p = self.player
        lucky = (p.has_relic("always_lucky") or p.lucky > 0
                 or getattr(p, "next_spin_lucky", False))
        if not p.has_relic("always_lucky") and not p.next_spin_lucky and p.lucky > 0:
            p.lucky -= 1
        if lucky:
            self._log("🍀 GLÜCKSDREH! Keine Pech-Symbole, bessere Chancen.")

        rig = p.has_relic("rigged_machine")
        force_wild = ((p.has_relic("reel_joker") and getattr(self, "_combat_first_spin", False))
                      or getattr(p, "next_spin_wild", False))
        force_triple = getattr(p, "next_spin_triple", False)
        if force_triple:
            self._log("🎰 JACKPOT ERZWUNGEN – Drilling!")
        self.slot_machine.spin(lucky_bonus=lucky, time_scale=self._anim_mul(),
                               rig_negatives=rig, force_wild=force_wild,
                               force_triple=force_triple)
        self._combat_first_spin = False
        # Manipulations-Flags des nächsten Drehs verbrauchen
        p.next_spin_lucky = False
        p.next_spin_wild = False
        p.next_spin_triple = False
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

        # Doppelter Einsatz: das Ergebnis nochmal anwenden
        if getattr(self.player, "next_spin_double", False):
            self.player.next_spin_double = False
            self._log("  💵 DOPPELTER EINSATZ – nochmal!")
            extra = self.slot_machine.evaluate(self.player, self.enemy)
            for eff in extra:
                self._log(f"  {eff}")
            self.slot_effects_shown = effects + ["💵 ×2"] + extra

        if is_triple:
            self._award("triple")
            if self.player.has_relic("vamp_tooth"):
                healed = self.player.heal_hp(10)
                if healed > 0:
                    self._log(f"🦷 Vampirzahn: Drilling heilt +{healed} HP!")
            audio.play("jackpot")
            self._do_shake(12)
            self._spawn_particles(590, 150, (255, 210, 80), count=30, speed=240, size=5)
            self._spawn_particles(590, 150, (255, 120, 90), count=14, speed=200, size=4)
        self._fx_enemy_hit(e_hp0 - self.enemy.hp)

        if self._enemy_is_down():
            # Kurzer Delay, damit man das Slot-Ergebnis noch sehen kann (TODO #6)
            self.slot_death_pending = True
            self.slot_death_timer = 1.8 * self._anim_mul()
            self.slot_done = True
        else:
            self.slot_done = True
    
    # ═══════════════════════════════════════════════
    # GEGNER-RUNDE
    # ═══════════════════════════════════════════════
    
    def _anim_mul(self):
        """Animations-Tempo: 'Schnell'-Option halbiert Wartezeiten."""
        return 0.5 if self.options.get("fast") else 1.0

    def _start_enemy_turn(self):
        self.state = STATE_ENEMY_TURN
        self.enemy_turn_timer = 1.5 * self._anim_mul()  # Sekunden bis Angriff
        self.enemy_turn_log = []
        self._log("⚔️ Gegner ist am Zug...")
    
    # ═══════════════════════════════════════════════
    # SLOT-MODUS (reines Slot-Aufbau-Spiel)
    # ═══════════════════════════════════════════════

    def _start_slotmode(self):
        self.slotrun = slotmode.SlotRun()
        self.slot_machine = SlotMachine(SCREEN_W // 2 - 170, 196)
        self._sm_spinning = False
        self._sm_pending = []
        self.state = STATE_SLOTMODE

    def _sm_spin_button(self):
        return pygame.Rect(SCREEN_W // 2 - 120, 452, 240, 56)

    def _sm_back_rect(self):
        return pygame.Rect(16, 16, 150, 38)

    def _sm_shop_layout(self):
        n = len(self.slotrun.shop) if self.slotrun else 0
        ow, gap = 210, 22
        total = n * ow + (n - 1) * gap
        sx = SCREEN_W // 2 - total // 2
        offers = [pygame.Rect(sx + i * (ow + gap), 360, ow, 168) for i in range(n)]
        return {
            "offers": offers,
            "reroll": pygame.Rect(SCREEN_W // 2 - 220, 556, 200, 46),
            "continue": pygame.Rect(SCREEN_W // 2 + 20, 556, 200, 46),
        }

    def _sm_spin(self):
        r = self.slotrun
        if not r or r.game_over or r.in_shop or self._sm_spinning or r.spins_left <= 0:
            return
        names = r.draw_symbols()
        self._sm_pending = names
        targets = [self._sm_by_name.get(n) for n in names]
        self.slot_machine.spin(time_scale=self._anim_mul(), targets=targets)
        self._sm_spinning = True
        audio.start_spin()

    def _sm_resolve(self):
        audio.stop_spin()
        r = self.slotrun
        total, _lines = r.resolve_spin(self._sm_pending)
        if r.in_shop:                       # Runde geknackt
            audio.play("jackpot"); audio.play("fanfare")
            self._do_shake(12)
            self._spawn_particles(SCREEN_W // 2, 250, (255, 210, 80), count=26,
                                  speed=220, size=5)
            if r.round >= 8:
                self._award("slot_master")
        elif r.game_over:
            audio.play("lose")
        else:
            audio.play("jackpot" if total >= 120 else "reel", 0.8)
            self._do_shake(min(12, 2 + total // 30))

    def _handle_slotmode_click(self, pos):
        r = self.slotrun
        if not r:
            self.state = STATE_MENU
            return
        if r.game_over:
            if self._sm_back_rect().collidepoint(pos) or \
               self._sm_spin_button().collidepoint(pos):
                audio.click(); self.state = STATE_MENU
            return
        if r.in_shop:
            lay = self._sm_shop_layout()
            for i, rect in enumerate(lay["offers"]):
                if i < len(r.shop) and rect.collidepoint(pos):
                    audio.play("gold" if r.buy(r.shop[i]) else "error")
                    return
            if lay["reroll"].collidepoint(pos):
                audio.play("gold" if r.reroll() else "error")
                return
            if lay["continue"].collidepoint(pos):
                audio.click(); r.next_round()
                return
            return
        # Spin-Phase
        if not self._sm_spinning and self._sm_spin_button().collidepoint(pos):
            self._sm_spin()
            return
        if self._sm_back_rect().collidepoint(pos):
            audio.click(); self.state = STATE_MENU

    def _music_for_state(self):
        """Passender Musik-Track je Spielzustand."""
        s = self.state
        ai = (self.act - 1) % len(ACT_THEMES)   # Akt-Index für akt-eigene Tracks
        if s in (STATE_PLAYER_TURN, STATE_SLOT_SPIN, STATE_ENEMY_TURN, STATE_REWARD):
            if self.enemy and getattr(self.enemy, "is_boss", False):
                return f"boss_a{ai}"
            return f"combat_a{ai}"
        if s in (STATE_MAP, STATE_REST, STATE_EVENT, STATE_ACT_CLEAR, STATE_SHOP):
            return f"explore_a{ai}"
        return "menu"

    def _update(self, dt):
        # Update fertig heruntergeladen & getauscht -> alte Version beenden
        if updater.progress.get("done"):
            self.running = False
            return
        # Musik passend zum Zustand umschalten (play_music ist günstig, wenn gleich)
        if not audio.is_muted():
            audio.play_music(self._music_for_state())

        # Animationen laufen immer (auch während Hit-Stop)
        self._update_particles(dt)
        # Erfolgs-Toasts ticken (laufen über jedem State weiter)
        if self.achievement_toasts:
            self.achievement_toasts = [[d, t - dt] for d, t in self.achievement_toasts
                                       if t - dt > 0]
        # Schwellen-Erfolge (billig, einmalig dank unlock-Sperre)
        if self.player:
            if self.player.gold >= 300:
                self._award("rich")
            if self.player.strength >= 10:
                self._award("muscles")
        if self.enemy:
            if getattr(self.enemy, "poison", 0) >= 15:
                self._award("poison_master")
            if getattr(self.enemy, "frost", 0) >= 10:
                self._award("frost_master")
            if getattr(self.enemy, "doom", 0) > 0:
                self._award("doom_master")
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

        elif self.state == STATE_SLOTMODE:
            if self._sm_spinning and self.slot_machine:
                prev = sum(self.slot_machine._reel_done)
                self.slot_machine.update()
                if sum(self.slot_machine._reel_done) > prev:
                    audio.play("reel", 0.7)
                if not self.slot_machine.spinning:
                    self._sm_spinning = False
                    self._sm_resolve()
    
    def _execute_enemy_turn(self):
        """Führt Gegner-Angriff aus"""
        hp_before = self.player.hp
        dodged = self.player.dodge and self.enemy.intent in ("attack", "heavy_attack")
        slot_boss_spin = (self.enemy.intent == "spin")
        logs = self.enemy.execute_turn(self.player)
        if slot_boss_spin:
            # Jackpot-Automat dreht -> Slot-Sound, Drilling = Jackpot + Shake
            triple = self.enemy.last_slot and len(set(self.enemy.last_slot)) == 1
            audio.play("jackpot" if triple else "reel", 0.85)
            self._do_shake(14 if triple else 6)
        for log in logs:
            self._log(log)

        # Ausweichen: Angriffsschaden komplett negieren
        if dodged:
            self.player.hp = hp_before
            self.player.dodge = False
            self._log("💨 Ausgewichen! Kein Schaden.")

        dmg_taken = hp_before - self.player.hp
        self._fx_player_hit(dmg_taken)

        # Phönixfeder ausgelöst?
        if self.player._phoenix_triggered:
            self.player._phoenix_triggered = False
            self._log("🔥🪶 PHÖNIXFEDER! Du wärst gestorben – überlebst mit 1 HP!")
            self._do_shake(14)

        # Dornenpanzer-Relik: reflektiert pauschal 5 Schaden bei Gegnerangriff
        if self.player.has_relic("thorns") and dmg_taken > 0 and self.enemy.is_alive():
            thorn = self.enemy.take_damage(5)
            self._log(f"🌵 Dornenpanzer: {thorn} Schaden zurück!")

        # Dornen-Status (Stachelhaut-Karte): reflektiert pro Treffer
        if self.player.thorns > 0 and dmg_taken > 0 and self.enemy.is_alive():
            thorn = self.enemy.take_damage(self.player.thorns)
            self._log(f"🌵 Dornen: {thorn} Schaden zurück!")

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

        if self.player.hp == 1:
            self._award("near_death")

        if not self.player.is_alive():
            self._award("first_death")
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
    
    def _award(self, aid):
        """Schaltet einen Erfolg frei und zeigt einen Toast (nur beim 1. Mal)."""
        if achievements.unlock(aid):
            self.achievement_toasts.append([achievements.get(aid), 4.5])
            # Meta-Unlock: Erfolg schaltet neue Karte/Relikt frei -> eigener Toast
            for kind, name in achievements.rewards_for(aid):
                label = "Neue Karte" if kind == "card" else "Neues Relikt"
                self.achievement_toasts.append([
                    {"emoji": "🔓", "name": f"{label}: {name}",
                     "desc": "Ab jetzt in Belohnungen zu finden!"}, 5.5])
            audio.play("relic", 0.8)

    def _enemy_defeated(self):
        """Gegner besiegt: Belohnung vorbereiten"""
        self.player.damage_dealt += self.enemy.max_hp
        self.player.enemies_defeated += 1

        # Trophäensammlung: +1 Stärke dauerhaft pro Boss
        if self.enemy.is_boss and self.player.has_relic("trophy"):
            self.player.strength += 1
            self._log("🏆 Trophäensammlung: +1 Stärke dauerhaft!")

        # Aasfresser: Heilung bei jedem Kill
        if self.player.has_relic("scavenger"):
            healed = self.player.heal_hp(max(1, self.player.max_hp // 10))
            if healed > 0:
                self._log(f"🦅 Aasfresser: +{healed} HP!")

        # Krähenfeder: Gold + Glück bei jedem Kill
        if self.player.has_relic("crow_feather"):
            self.player.add_gold(5); self.player.lucky += 1
            self._log("🪶 Krähenfeder: +5 Gold, +1 Glücksrunde!")

        # ─── Erfolge ───
        self._award("first_blood")
        if self.enemy.is_boss:
            self._award("boss_kill")
            if self.player.hp >= self.player.max_hp:
                self._award("flawless_boss")
            if len(self.player.deck + self.player.discard + self.player.hand) <= 8:
                self._award("slim_deck")
        if self.enemy.is_elite:
            self._award("elite_kill")
        if self.floor_num >= 20:
            self._award("marathon")

        # Goldener Finger: +30% Gold
        gold = self.enemy.get_gold_reward()
        if self.player.has_relic("gold_boost"):
            gold = int(gold * 1.3)
        if (self.daily_mod or {}).get("gold_mult"):
            gold = int(gold * self.daily_mod["gold_mult"])
        self.gold_reward = gold
        self.player.add_gold(gold)
        self._log(f"🏆 {self.enemy.name} besiegt! +{gold} Gold!")
        audio.play("gold", 0.7)
        self._spawn_particles(*self.ENEMY_FX, color=(255, 210, 80), count=22, speed=200, size=4)

        # Kleine Heilung nach jedem normalen Kampf (fairer)
        if not self.enemy.is_boss and not self.enemy.is_elite:
            healed = self.player.heal_hp(max(4, self.player.max_hp // 12))
            if healed > 0:
                self._log(f"🌿 Verschnaufpause: +{healed} HP")

        # Herzstein: Heilung bei Kill
        if self.player.has_relic("heal_on_kill"):
            healed = self.player.heal_hp(8)
            if healed > 0:
                self._log(f"❤️ Herzstein: +{healed} HP!")

        # Drei Karten zur Wahl – nach Seltenheit gewichtet (keine Flüche)
        self.reward_cards = self._weighted_reward_cards(3)

        # Relikt-Belohnung bei Elite & Boss: 3 zur Auswahl (Build planen)
        self.reward_relic = None
        self.relic_choices = []
        self.relic_choice_rects = []
        self.hovered_relic_idx = None
        if self.enemy.is_elite or self.enemy.is_boss:
            self.relic_choices = self._roll_relic_choices(3)

        if self.relic_choices:
            self.state = STATE_RELIC_REWARD
        else:
            self.state = STATE_REWARD

    def _weighted_reward_cards(self, n=3):
        """Wählt n verschiedene Karten gewichtet nach Seltenheit aus"""
        boss = bool(self.enemy and (self.enemy.is_elite or self.enemy.is_boss))
        weights = {
            "common":   40 if boss else 68,
            "uncommon": 38 if boss else 27,
            "rare":     22 if boss else 5,
        }
        # Flüche sind separat; Meta-Unlocks: gesperrte Karten erst nach Erfolg.
        # Karten-Pool: jede Karte darf man bis zu 3x besitzen (mehrmals, aber
        # nicht zu oft) – Karten mit bereits 3 Kopien fallen aus dem Pool.
        owned_counts = {}
        for c in (self.player.deck + self.player.discard + self.player.hand):
            owned_counts[c.name] = owned_counts.get(c.name, 0) + 1
        avail = [c for c in CARD_DEFINITIONS
                 if achievements.content_unlocked("card", c["name"])
                 and owned_counts.get(c["name"], 0) < 3]
        # Klassen-Gewichtung: passende Archetyp-Karten häufiger (v1.17)
        fav = CLASS_FAVORED.get(getattr(self.player, "class_id", None), set())
        chosen = []
        for _ in range(min(n, len(avail))):
            ws = []
            for c in avail:
                w = weights.get(c.get("rarity", "common"), 10)
                if c.get("effect") in fav:
                    w = int(w * 2.5)
                ws.append(w)
            pick = random.choices(avail, weights=ws, k=1)[0]
            chosen.append(pick)
            avail.remove(pick)
        return [Card(c) for c in chosen]

    def _roll_relic_choices(self, n=3):
        """Wählt bis zu n verschiedene, noch nicht besessene Relikte zur Auswahl."""
        owned = {r["id"] for r in self.player.relics}
        available = [r for r in RELIC_DEFINITIONS if r["id"] not in owned
                     and achievements.content_unlocked("relic", r["name"])]
        if not available:
            return []
        return random.sample(available, min(n, len(available)))

    def _pick_relic_reward(self, idx):
        """Spieler wählt eines der angebotenen Relikte aus."""
        if not (0 <= idx < len(self.relic_choices)):
            return
        relic = self.relic_choices[idx]
        self.player.add_relic(relic)
        self.reward_relic = relic
        self._log(f"💠 Relikt erhalten: {relic['emoji']} {relic['name']}!")
        if len(self.player.relics) >= 5:
            self._award("relic_5")
        audio.play("relic")
        self.relic_choices = []
        self.relic_choice_rects = []
        self.state = STATE_REWARD

    def _grant_random_relic(self):
        """Vergibt ein zufälliges noch nicht besessenes Relikt"""
        owned = {r["id"] for r in self.player.relics}
        available = [r for r in RELIC_DEFINITIONS if r["id"] not in owned
                     and achievements.content_unlocked("relic", r["name"])]
        if not available:
            return None
        relic = random.choice(available)
        self.player.add_relic(relic)
        if len(self.player.relics) >= 5:
            self._award("relic_5")
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
            p.perm_strength += val; p.strength += val; msg = f"+{val} Stärke DAUERHAFT!"
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
        elif eff == "casino_double_or_nothing":
            if p.gold <= 0:
                msg = "Du hast nichts zum Setzen. Der Croupier lacht."
            elif random.random() < 0.5:
                won = p.gold
                p.add_gold(won)
                msg = f"🎉 ROT! Gold verdoppelt: +{won} Gold!"
                audio.play("jackpot")
            else:
                lost = p.gold
                p.gold = 0
                msg = f"💸 SCHWARZ. {lost} Gold – einfach weg. Das Haus nickt."
        elif eff == "casino_blood_poker":
            p.take_damage(20, ignore_block=True)
            if random.random() < 0.6:
                r = self._grant_random_relic()
                msg = (f"−20 HP, aber du gewinnst: {r['emoji']} {r['name']}!" if r
                       else "−20 HP. Gewonnen – aber alle Relikte hast du schon.")
            else:
                msg = "−20 HP. Dein Blatt war Müll. Der Tisch schweigt."
        elif eff == "casino_mystery_box":
            if not p.spend_gold(val):
                msg = "Nicht genug Gold für die Box!"
            else:
                roll = random.random()
                if roll < 0.30:
                    cd = random.choice([c for c in CARD_DEFINITIONS
                                        if achievements.content_unlocked("card", c["name"])])
                    p.add_card_to_deck(cd)
                    msg = f"📦 In der Box: Karte '{cd['name']}'!"
                elif roll < 0.55:
                    r = self._grant_random_relic()
                    msg = f"📦 In der Box: {r['emoji']} {r['name']}!" if r else "📦 Leer. Alle Relikte schon da."
                elif roll < 0.80:
                    h = p.heal_hp(25)
                    msg = f"📦 Heiltrank! +{h} HP."
                else:
                    self._add_curse()
                    msg = "📦 Ein FLUCH springt heraus. Reingefallen."
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
        self.shop_gamble_count = 0    # Glücksrad-Einsatz beim Betreten zurücksetzen

        # Preise steigen mit der Tiefe (Gold-Sink, TODO #1)
        self._shop_price_mult = 1.0 + (self.floor_num - 1) * 0.05

        def sc(c):
            return int(round(c * self._shop_price_mult))

        forge = {"id": "upgrade_card", "name": "Schmiede", "emoji": "⚒️", "cost": sc(50),
                 "desc": "Werte eine Karte dauerhaft auf (+50% Werte)."}
        items = [forge]
        # Relikt-Händler: ein kaufbares Relikt (großer Gold-Sink)
        self._shop_relic = self._pick_shop_relic()
        if self._shop_relic:
            r = self._shop_relic
            items.append({"id": "buy_relic", "name": f"Relikt: {r['name']}",
                          "emoji": r.get("emoji", "💠"), "cost": sc(110),
                          "desc": r.get("desc", "Ein mächtiges Relikt.")})
        pool = [dict(it, cost=sc(it["cost"])) for it in SHOP_FIXED_ITEMS]
        random.shuffle(pool)
        items += pool[: max(0, 5 - len(items))]
        self.shop_items = items
        self.shop_reroll_cost = sc(15)

    def _pick_shop_relic(self):
        """Wählt ein kaufbares Relikt für den Relikt-Händler (oder None)."""
        owned = {r["id"] for r in self.player.relics}
        avail = [r for r in RELIC_DEFINITIONS if r["id"] not in owned
                 and achievements.content_unlocked("relic", r["name"])]
        return random.choice(avail) if avail else None

    def _reroll_shop(self):
        """Mischt die zufälligen Shop-Items neu (kostet Gold, wird teurer)."""
        cost = self.shop_reroll_cost
        if self.player.gold < cost:
            self._shop_message("❌ Nicht genug Gold zum Neumischen!"); audio.play("error", 0.6)
            return
        self.player.spend_gold(cost)
        pm = getattr(self, "_shop_price_mult", 1.0)
        sc = lambda c: int(round(c * pm))
        keep = [it for it in self.shop_items if it["id"] in ("upgrade_card", "buy_relic")]
        pool = [dict(it, cost=sc(it["cost"])) for it in SHOP_FIXED_ITEMS]
        random.shuffle(pool)
        self.shop_items = keep + pool[: max(0, 5 - len(keep))]
        self.shop_reroll_cost = cost + sc(10)
        audio.play("gold")
    
    def _shop_message(self, text):
        self.shop_message = text
        self.shop_message_timer = 2.0
    
    def _buy_shop_item(self, item):
        """Kauft ein Shop-Item (jedes nur 1x pro Shop-Besuch)"""
        item_id = item["id"]
        cost = item["cost"]
        if self.player.has_relic("counterfeit"):   # Falschgeld: 25% Rabatt
            cost = int(round(cost * 0.75))

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
            self.grid_scroll = 0
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
            self.grid_scroll = 0
            self.shop_pending_cost = cost
            return

        # Relikt-Händler: gekauftes Relikt direkt vergeben
        if item_id == "buy_relic":
            self.player.spend_gold(cost)
            r = getattr(self, "_shop_relic", None)
            if r:
                self.player.add_relic(r)
                if len(self.player.relics) >= 5:
                    self._award("relic_5")
                audio.play("relic")
                self._shop_message(f"💠 {r['name']} gekauft!")
            self.shop_purchased.add(item_id)
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
            p.perm_strength += 2; p.strength += 2
            self._shop_message("⚡ +2 Stärke DAUERHAFT!")
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
    
    def _gamble_bet(self):
        """Aktueller Glücksrad-Einsatz – steigt mit jeder Drehung pro Shop-Besuch.
        Würfelbecher-Relikt friert den Einsatz bei 25 ein."""
        if self.player and self.player.has_relic("gamble_discount"):
            bet = 25
        else:
            bet = 25 + self.shop_gamble_count * 15
        if self.player and self.player.has_relic("counterfeit"):
            bet = int(round(bet * 0.75))
        return bet

    def _gamble(self):
        """Glücksrad im Shop: steigender Einsatz, House-Edge (~−14% Erwartungswert),
        Auszahlung skaliert mit dem Einsatz. Kein Endlos-Geld-Exploit mehr."""
        bet = self._gamble_bet()
        if self.player.gold < bet:
            self._shop_message(f"❌ Einsatz {bet} Gold – nicht genug!")
            return

        self.player.spend_gold(bet)
        self.shop_gamble_count += 1
        audio.play("reel", 0.8)
        roll = random.random()
        # Auszahltabelle (brutto, Einsatz ist bereits weg). Erwartungswert ~0.86×
        # -> das Haus gewinnt langfristig. Selten großer Jackpot bleibt drin.
        if roll < 0.55:
            self._shop_message(f"🎰 NICHTS. Das Haus gewinnt. (−{bet} Gold)")
        elif roll < 0.77:
            win = bet  # Einsatz zurück
            self.player.add_gold(win)
            self._shop_message(f"🎰 Einsatz zurück (+{win} Gold)")
        elif roll < 0.92:
            win = bet * 2
            self.player.add_gold(win)
            self._shop_message(f"🎰 GEWINN! +{win} Gold (2×)")
        elif roll < 0.98:
            win = bet * 3
            self.player.add_gold(win)
            self._shop_message(f"🎰 GROSSER GEWINN! +{win} Gold (3×)!")
        else:
            mega = roll >= 0.995          # sehr seltener Mega-Jackpot
            mult = 15 if mega else 8
            win = bet * mult
            self.player.add_gold(win)
            label = "MEGA-JACKPOT" if mega else "JACKPOT"
            self._shop_message(f"🎰💰 {label}!!! +{win} Gold ({mult}×)!!!")
            self._award("gamble_jackpot")
            audio.play("jackpot")
            self._spawn_particles(self.shop_gamble_rect.centerx if self.shop_gamble_rect else 300,
                                  430, (255, 210, 80), count=26 + (20 if mega else 0),
                                  speed=220, size=4)
    
    def _leave_shop(self):
        """Verlässt den Shop, zurück zur Karte"""
        self.shop_remove_mode = False
        self.shop_upgrade_mode = False
        audio.play("click")
        self._finish_node()
    
    def _save_highscore(self, won=False):
        """Speichert den Punktestand (nur einmal pro Run)"""
        if self.score_saved:
            return
        self.last_rank, self.last_score, self.last_is_record = add_highscore(
            self.player, self.floor_num, won=won)
        self.highscores = load_highscores()
        self.score_saved = True
        savegame.delete_save()   # Run beendet -> Speicherstand entfernen

        # Lifetime-Stats + Tages-Challenge melden
        self.lifetime_stats = stats.report_run(
            self.floor_num, self.player.enemies_defeated, self.player.gold_earned)
        if self.daily_mode:
            self.daily_result = daily.report_run(self.last_score)
            try:
                if daily.get_streak() >= 3:
                    self._award("daily_streak")
            except Exception:
                pass

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
            "burn": p.burn, "strength": p.strength, "perm_strength": p.perm_strength,
            "mult": p.mult, "lucky": p.lucky,
            "poison": p.poison, "regen": p.regen, "thorns": p.thorns,
            "vulnerable": p.vulnerable, "rage": p.rage, "focus": p.focus,
            "class_id": p.class_id, "phoenix_used": p.phoenix_used,
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
                "enemies_defeated": p.enemies_defeated, "best_combo": p.best_combo,
            },
        }

    def _deserialize_player(self, d):
        # Defensiv: JEDES Feld per .get mit Default -> alte Saves ohne neue
        # Felder bleiben IMMER ladbar (siehe savegame.load_save).
        p = Player()  # baut Defaults (Starterdeck, volle HP) – selektiv überschrieben
        p.max_hp = d.get("max_hp", p.max_hp); p.hp = d.get("hp", p.hp)
        p.gold = d.get("gold", p.gold); p.block = d.get("block", 0)
        p.energy = d.get("energy", p.energy); p.max_energy = d.get("max_energy", p.max_energy)
        p.burn = d.get("burn", 0); p.strength = d.get("strength", 0); p.lucky = d.get("lucky", 0)
        p.perm_strength = d.get("perm_strength", d.get("strength", 0))
        p.mult = d.get("mult", 1.0)
        p.poison = d.get("poison", 0); p.regen = d.get("regen", 0); p.thorns = d.get("thorns", 0)
        p.vulnerable = d.get("vulnerable", 0); p.rage = d.get("rage", 0); p.focus = d.get("focus", 0)
        p.class_id = d.get("class_id")
        p.phoenix_used = d.get("phoenix_used", False)
        p.shield_up = d.get("shield_up", False); p.reflect = d.get("reflect", False)
        p.coin_rain_active = d.get("coin_rain_active", False)
        p.next_free_card = d.get("next_free_card", False)
        p._total_damage_taken = d.get("total_damage_taken", 0)
        p.bonus_spins = d.get("bonus_spins", 0)
        if "deck" in d:    p.deck = [self._deserialize_card(c) for c in d["deck"]]
        if "hand" in d:    p.hand = [self._deserialize_card(c) for c in d["hand"]]
        if "discard" in d: p.discard = [self._deserialize_card(c) for c in d["discard"]]
        if "relics" in d:  p.relics = [dict(r) for r in d["relics"]]
        st = d.get("stats", {})
        p.damage_dealt = st.get("damage_dealt", 0)
        p.gold_earned = st.get("gold_earned", 0)
        p.slots_spun = st.get("slots_spun", 0)
        p.chickens_summoned = st.get("chickens_summoned", 0)
        p.enemies_defeated = st.get("enemies_defeated", 0)
        p.best_combo = st.get("best_combo", 0)
        return p

    def _serialize_enemy(self, e):
        return {
            "name": e.name, "hp": e.hp, "max_hp": e.max_hp, "damage": e.damage,
            "armor": e.armor, "block": e.block, "gold_reward": list(e.gold_reward),
            "color": list(e.color), "tooltip": e.tooltip, "tier": e.tier,
            "is_boss": e.is_boss, "is_elite": e.is_elite, "mechanic": e.mechanic,
            "asset": e.asset,
            "burn": e.burn, "weakened": e.weakened,
            "poison": e.poison, "vulnerable": e.vulnerable,
            "frost": e.frost, "stunned": e.stunned, "doom": e.doom, "marked": e.marked,
            "intent": e.intent, "intent_value": e.intent_value,
            "undying_used": e._undying_used, "jam_next": e.jam_next,
            "turn_count": e.turn_count,
        }

    def _deserialize_enemy(self, d):
        # Defensiv: jedes Feld mit Default -> Saves bleiben immer ladbar.
        hp = d.get("hp", 30)
        etype = {
            "name": d.get("name", "Gegner"), "hp": hp, "max_hp": d.get("max_hp", hp),
            "damage": d.get("damage", 6), "armor": d.get("armor", 0),
            "gold_reward": tuple(d.get("gold_reward", (8, 15))),
            "color": tuple(d.get("color", ENEMY_COLOR)),
            "tooltip": d.get("tooltip", ""), "tier": d.get("tier", 1),
            "is_boss": d.get("is_boss", False), "is_elite": d.get("is_elite", False),
            "mechanic": d.get("mechanic"), "asset": d.get("asset"),
        }
        e = Enemy(etype)
        e.block = d.get("block", 0); e.burn = d.get("burn", 0); e.weakened = d.get("weakened", 0)
        e.poison = d.get("poison", 0); e.vulnerable = d.get("vulnerable", 0)
        e.frost = d.get("frost", 0); e.stunned = d.get("stunned", 0)
        e.doom = d.get("doom", 0); e.marked = d.get("marked", 0)
        e.intent = d.get("intent", "attack"); e.intent_value = d.get("intent_value", e.damage)
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

    def _autosave(self):
        """Stiller Autosave (zwischen Knoten). Niemals crashen."""
        if not self.player:
            return
        try:
            savegame.write_save(self._serialize_run())
        except Exception as exc:
            print(f"[autosave] {exc}")

    def _load_run(self):
        """Lädt einen gespeicherten Run. Saves sind versionsunabhängig gültig;
        bei einem echten Defekt fällt es sauber ins Menü zurück (ohne den
        Speicherstand zu löschen)."""
        data = savegame.load_save()
        if not data or "player" not in data:
            return
        try:
            self._load_run_unsafe(data)
        except Exception as exc:
            # Schutznetz: niemals crashen, niemals den Save löschen
            print(f"[load_run] Konnte Save nicht laden: {exc}")
            self.player = None
            self.enemy = None
            self.state = STATE_MENU

    def _load_run_unsafe(self, data):
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
    ENEMY_FX = (1000, 210)   # Gegner rechts
    PLAYER_FX = (230, 210)   # Spieler-Avatar links

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
        self._spawn_particles(x, y, (255, 70, 70), count=min(24, 6 + dmg // 2),
                              speed=130 + dmg * 2, size=4)
        self._do_shake(min(13.0, 3 + dmg * 0.2))
        self._do_hitstop(min(0.1, 0.02 + dmg * 0.002))
        self._add_damage_number(f"-{dmg}", x, y - 40, (255, 90, 90))

    def _fx_block(self, amount):
        if amount <= 0:
            return
        audio.play("block", 0.7)
        x, y = self.PLAYER_FX
        self._spawn_particles(x, y, (90, 160, 230), count=8, speed=120, size=3)

    def _fx_heal(self, amount):
        if amount <= 0:
            return
        audio.play("heal", 0.7)
        x, y = self.PLAYER_FX
        self._spawn_particles(x, y, (80, 220, 120), count=10, speed=130, size=3)
        self._add_damage_number(f"+{amount}", x, y - 40, (90, 230, 130))

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
    
    def _scene_for_state(self):
        """Hintergrund-Szene je Zustand: im Run akt-abhängig, sonst Kneipe."""
        in_run = getattr(self, "player", None) and self.state in (
            STATE_MAP, STATE_REST, STATE_ACT_CLEAR, STATE_PLAYER_TURN,
            STATE_SLOT_SPIN, STATE_ENEMY_TURN, STATE_REWARD, STATE_EVENT, STATE_SHOP)
        if not in_run:
            return "bg_kneipe"
        # Hintergrund des aktuellen Akt-Themas (Fallback bg_void, falls Sprite fehlt)
        bg = self._act_theme()[2]
        import assets
        return bg if assets.has("ui", bg) else "bg_void"

    def _draw(self):
        self.ui.set_scene(self._scene_for_state())
        if self.state == STATE_MENU:
            self.ui.draw_main_menu(self._compute_menu_layout())
            # Update-Button, wenn eine neuere Version verfügbar ist
            if updater.status.get("available"):
                self.update_btn_rect = self.ui.draw_update_button(updater.status.get("version"))
            else:
                self.update_btn_rect = None

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
                             self.hovered_node, self.player, self.act, self.map_message,
                             act_name=self._act_theme()[0])
            if self.daily_mode and self.daily_mod:
                self.ui._chip(f"📅 {self.daily_mod['name']}: {self.daily_mod['desc']}",
                              self.ui.font_tiny, SCREEN_W // 2 - 280, 8,
                              text_col=CYAN, fill=(15, 45, 55, 220))

        elif self.state == STATE_REST:
            self.ui.draw_rest(self.player, self._compute_rest_layout())

        elif self.state == STATE_ACT_CLEAR:
            self.ui.draw_act_clear(self._cleared_act, self.player,
                                   next_act_name=self._act_theme()[0])

        elif self.state in (STATE_PLAYER_TURN, STATE_SLOT_SPIN, STATE_ENEMY_TURN):
            self._draw_combat()
        
        elif self.state == STATE_RELIC_REWARD:
            self._draw_combat_bg()
            self.relic_choice_rects = self.ui.draw_relic_reward(
                self.relic_choices, self.player, self.hovered_relic_idx
            )

        elif self.state == STATE_REWARD:
            self._draw_combat_bg()  # Hintergrund
            self._draw_reward()

        elif self.state == STATE_EVENT:
            self._draw_event()

        elif self.state == STATE_SHOP:
            self._draw_shop()
        
        elif self.state == STATE_SCORES:
            self._draw_scores()

        elif self.state == STATE_ACHIEVEMENTS:
            self.achievements_back_rect = self.ui.draw_achievements(
                achievements.DEFS, achievements.is_unlocked, achievements.progress())

        elif self.state == STATE_CLASS_SELECT:
            self.class_select_rects, self.class_back_rect = self.ui.draw_class_select(
                CLASS_DEFINITIONS, daily=self.pending_daily)
        
        elif self.state == STATE_GAME_OVER:
            self.ui.draw_game_over(self.player, self.floor_num,
                                   self.last_score, self.last_rank,
                                   lifetime=self.lifetime_stats,
                                   daily_result=self.daily_result)

        elif self.state == STATE_VICTORY:
            self.ui.draw_victory(self.player, self.last_score, self.last_rank)

        elif self.state == STATE_SLOTMODE:
            self.ui.draw_slotmode(self.slotrun, self.slot_machine, self._sm_spinning,
                                  self._sm_spin_button(), self._sm_shop_layout(),
                                  self._sm_back_rect())

        # Globale Overlays (Schmiede/Verbrennen) über dem aktuellen Screen
        if self.shop_remove_mode:
            self.shop_remove_rects = self.ui.draw_card_grid(
                self.player, "🔥 Welche Karte verbrennen?", ORANGE, only_upgradeable=False,
                scroll=self.grid_scroll)
        elif self.shop_upgrade_mode:
            self.shop_upgrade_rects = self.ui.draw_card_grid(
                self.player, "⚒️ Welche Karte aufwerten?", GOLD, only_upgradeable=True,
                scroll=self.grid_scroll)

        # Partikel über allem
        self._draw_particles()
        # Erfolgs-Toasts (oben rechts, über allem)
        if self.achievement_toasts:
            self.ui.draw_achievement_toasts(self.achievement_toasts)
        # Mute-Indikator
        if audio.is_muted():
            self.ui._text("🔇", self.ui.font_small, GREY, SCREEN_W - 30, 6)
        # Update-Fortschritt über allem
        if updater.progress.get("active") or updater.progress.get("error"):
            self.ui.draw_update_overlay(updater.progress)

    def _draw_combat_bg(self):
        """Zeichnet den Kampf-Hintergrund ohne UI-Elemente"""
        self.ui.draw_background()
    
    def _draw_combat(self):
        """Hauptkampf-Bildschirm"""
        self.ui.draw_background()

        # Status-Leiste oben
        self.ui.draw_status_bar(self.player, self.enemy, self.floor_num, self.turn_num)

        # Spieler-Avatar LINKS (unter der Spieler-HP)
        self.ui.draw_player_side(self.player, 84, 96, 290, 274)

        # Reliktleiste ganz links (links neben dem Avatar)
        self.ui.draw_relic_bar(self.player, 8, 112)

        # Gegner RECHTS (unter der Gegner-HP)
        if self.enemy:
            self.ui.draw_enemy(self.enemy, SCREEN_W - 360, 96, 320, 274)

        # Slot-Maschine nur in Slot-Phase (TODO #8)
        if self.state == STATE_SLOT_SPIN and self.slot_machine:
            self.slot_machine.draw(self.screen,
                                   self.ui.font_title, self.ui.font_large,
                                   self.ui.font_small, self.ui.font_tiny)

        # Slot-Effekte nur in Slot-Phase
        if self.state == STATE_SLOT_SPIN and self.slot_effects_shown:
            self._draw_slot_effects()

        # Kampf-Log (mittig)
        self.ui.draw_combat_log(self.combat_log, 410, 318, 380, 168, scroll=self.log_scroll)
        
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

        # Buff-/Relikt-Tooltips ganz zuletzt (über Karten & Avataren, TODO #6)
        self.ui.draw_pending_buff_tooltip()
        self.ui.draw_pending_relic_tooltip()

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
        
        # "Slot drehen"-Button (= Runde beenden) – mittig über dem Kampflog
        btn_w, btn_h = 210, 48
        self.ui.draw_slot_button(SCREEN_W//2 - btn_w//2, 240, btn_w, btn_h, pulsing=True)

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
        # Gegner schon besiegt (auch wenn noch Spins offen wären): Sieg-Hinweis,
        # kein Dreh-Button mehr.
        enemy_down = self.slot_death_pending or (self.enemy is not None and self.enemy.hp <= 0)
        if enemy_down:
            win_txt = self.ui.font_title.render("🏆 GEGNER BESIEGT!", True, GOLD)
            self.screen.blit(win_txt, (SCREEN_W//2 - win_txt.get_width()//2, 735))
        elif self.spins_remaining > 0 and not self.slot_machine.spinning:
            self.ui.draw_button(
                f"🎰 DREHEN! ({self.spins_remaining}x)",
                SCREEN_W//2 - 80, spin_y, 160, 45,
                color=GOLD, pulsing=True
            )
        elif self.slot_machine.spinning:
            self.ui.draw_button("Dreht ...", SCREEN_W//2 - 80, spin_y, 160, 45,
                               color=GREY_DARK, disabled=True)

        if not enemy_down and self.spins_remaining == 0 and not self.slot_machine.spinning:
            if not self.slot_done:
                # 0 Spins (z.B. durch Slot-Jam) -> Hinweis statt leerer Phase
                hint = self.ui.font_small.render("🎰 Automat blockiert – keine Drehung!",
                                                 True, ORANGE)
                self.screen.blit(hint, (SCREEN_W//2 - hint.get_width()//2, 700))
            self.ui.draw_button("Weiter", SCREEN_W//2 - 80, 735, 160, 40,
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
        prog = max(0, self.enemy_turn_timer / (1.5 * self._anim_mul()))
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
        (self.shop_item_rects, self.shop_gamble_rect, self.shop_leave_rect,
         self.shop_reroll_rect) = self.ui.draw_shop(
            self.shop_items, self.player, self.shop_message, self.shop_purchased,
            gamble_bet=self._gamble_bet(),
            reroll_cost=getattr(self, "shop_reroll_cost", 0))

    def _draw_scores(self):
        """Highscore-Bildschirm"""
        self.scores_back_rect = self.ui.draw_scores(self.highscores)
