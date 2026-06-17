"""UI-Renderer: Alle Zeichenfunktionen für das Spiel (modernes Design)"""

import pygame
import math
from constants import *
import mapgen
import assets
import daily
import achievements
import slotmode


def _lerp(a, b, t):
    return a + (b - a) * t


def _lerp_color(c1, c2, t):
    return (int(_lerp(c1[0], c2[0], t)),
            int(_lerp(c1[1], c2[1], t)),
            int(_lerp(c1[2], c2[2], t)))


def _lighten(c, f=0.25):
    return (min(255, int(c[0] + (255 - c[0]) * f)),
            min(255, int(c[1] + (255 - c[1]) * f)),
            min(255, int(c[2] + (255 - c[2]) * f)))


def _darken(c, f=0.25):
    return (max(0, int(c[0] * (1 - f))),
            max(0, int(c[1] * (1 - f))),
            max(0, int(c[2] * (1 - f))))


class UIRenderer:
    """Zentrale Klasse für alle UI-Darstellungen"""

    def __init__(self, screen):
        self.screen = screen
        self.w = SCREEN_W
        self.h = SCREEN_H

        # Fonts (Segoe UI Emoji rendert Text UND Emojis sauber unter Windows)
        self.font_huge   = pygame.font.SysFont("Segoe UI Emoji", 44, bold=True)
        self.font_h1     = pygame.font.SysFont("Segoe UI Emoji", 30, bold=True)
        self.font_title  = pygame.font.SysFont("Segoe UI Emoji", 22, bold=True)
        # RAM-Sparen: large teilt sich das Font-Objekt mit h1 (Emoji-Fonts kosten
        # je ~8 MB). 'large' wird nur dekorativ/selten genutzt -> 30px bold reicht.
        self.font_large  = self.font_h1
        self.font_medium = pygame.font.SysFont("Segoe UI Emoji", 19, bold=True)
        self.font_small  = pygame.font.SysFont("Segoe UI Emoji", 15)
        self.font_tiny   = pygame.font.SysFont("Segoe UI Emoji", 13)
        # micro + nano teilen sich ein 10px-Objekt (spart ein weiteres Font-Objekt).
        # Bleibt als kleine Tooltip-Fallback-Stufe erhalten, ohne Überlauf-Risiko.
        self._font_micro = pygame.font.SysFont("Segoe UI Emoji", 10)
        self._font_nano  = self._font_micro

        self._anim_t = 0.0
        # Logische Mausposition (in der 1200×800-Canvas), wird jedes Frame
        # von game.run() gesetzt nachdem der Viewport-Transform berechnet wurde.
        self._mouse = (0, 0)

        # Caches für teure Surfaces
        self._panel_cache = {}
        self._shadow_cache = {}
        self._grad_cache = {}
        self._text_cache = {}   # gerenderte Text-Surfaces (vermeidet Ruckler)

        self._build_background()

    def tick(self, dt):
        self._anim_t += dt

    # ═══════════════════════════════════════════════
    # LOW-LEVEL HELFER (modernes Aussehen)
    # ═══════════════════════════════════════════════

    def set_scene(self, scene_name):
        """Wechselt den Hintergrund (z.B. je Akt). Gecacht -> günstig."""
        if getattr(self, "_scene_name", None) == scene_name:
            return
        self._scene_name = scene_name
        cache = getattr(self, "_scene_cache", None)
        if cache is None:
            cache = self._scene_cache = {}
        if scene_name not in cache:
            cache[scene_name] = self._build_scene(scene_name)
        self._bg = cache[scene_name]

    def _build_background(self):
        """Initialer Hintergrund + einmalige Deko-Glyphen."""
        self._scene_cache = {}
        self._scene_name = "bg_kneipe"
        self._scene_cache["bg_kneipe"] = self._build_scene("bg_kneipe")
        self._bg = self._scene_cache["bg_kneipe"]
        # Schwebende Deko-Glyphen EINMAL vorrendern (scene-unabhängig)
        self._bg_glyphs = []
        for g in ["♠", "♥", "♦", "♣", "🎰", "💰", "🍀", "⭐"]:
            surf = self.font_large.render(g, True, _lighten(BG_TOP, 0.12))
            surf.set_alpha(26)
            self._bg_glyphs.append(surf)

    def _build_scene(self, scene_name):
        """Baut eine Hintergrund-Szene (gemaltes Bild ODER Gradient) mit Vignette."""
        bg = pygame.Surface((self.w, self.h)).convert()
        scene = assets.load("ui", scene_name)
        if scene:
            # Gemalte Kneipen-Szene, abgedunkelt für Text-Kontrast
            bg.blit(pygame.transform.smoothscale(scene, (self.w, self.h)), (0, 0))
            dark = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
            dark.fill((6, 4, 14, 150))
            bg.blit(dark, (0, 0))
        else:
            for y in range(self.h):
                t = y / self.h
                pygame.draw.line(bg, _lerp_color(BG_TOP, BG_BOTTOM, t), (0, y), (self.w, y))
            # Weiche farbige Lichthöfe für Tiefe
            for (cx, cy, r, col, a) in [
                (self.w * 0.22, self.h * 0.18, 360, (90, 60, 160), 26),
                (self.w * 0.85, self.h * 0.30, 420, (160, 110, 40), 22),
                (self.w * 0.55, self.h * 0.95, 460, (50, 40, 110), 24),
            ]:
                halo = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
                for i in range(10):
                    rr = int(r * (1 - i / 10))
                    pygame.draw.circle(halo, (*col, int(a * (i + 1) / 10 / 3)),
                                       (r, r), rr)
                bg.blit(halo, (cx - r, cy - r))

        # Vignette (klein berechnet, hochskaliert = weich)
        sw, sh = 80, 53
        vig = pygame.Surface((sw, sh), pygame.SRCALPHA)
        for y in range(sh):
            for x in range(sw):
                dx = (x / sw - 0.5) * 2
                dy = (y / sh - 0.5) * 2
                d = min(1.0, math.sqrt(dx * dx + dy * dy) / 1.18)
                a = int(max(0, (d - 0.45)) / 0.55 * 165)
                if a > 0:
                    vig.set_at((x, y), (0, 0, 0, a))
        vig = pygame.transform.smoothscale(vig, (self.w, self.h))
        bg.blit(vig, (0, 0))

        # Akzentlinien oben/unten
        pygame.draw.line(bg, _darken(ACCENT, 0.4), (0, 0), (self.w, 0), 2)
        pygame.draw.line(bg, _darken(ACCENT, 0.55), (0, self.h - 1), (self.w, self.h - 1), 2)
        return bg

    def draw_background(self):
        """Zeichnet den vorberechneten Hintergrund + dezente Animation"""
        self.screen.blit(self._bg, (0, 0))
        # Schwebende, sehr dezente Symbole (vorgerenderte Surfaces, nur bewegt)
        t = self._anim_t
        for i, surf in enumerate(self._bg_glyphs):
            ph = i * 1.7
            x = (math.sin(t * 0.12 + ph) * 0.5 + 0.5) * self.w
            y = ((t * 14 + i * 110) % (self.h + 100)) - 50
            self.screen.blit(surf, (x, y))

    def _shadow(self, rect, radius=14, spread=10, alpha=120, dy=7):
        """Weicher Schlagschatten unter einem (gerundeten) Rechteck"""
        x, y, w, h = rect
        key = (w, h, radius, spread, alpha)
        surf = self._shadow_cache.get(key)
        if surf is None:
            surf = pygame.Surface((w + spread * 2, h + spread * 2), pygame.SRCALPHA)
            layers = 6
            for i in range(layers):
                f = (i + 1) / layers
                a = int(alpha * (f ** 2) / layers * 2.2)
                inset = int(spread * (1 - f))
                pygame.draw.rect(surf, (0, 0, 0, a),
                                 (inset, inset, w + (spread - inset) * 2, h + (spread - inset) * 2),
                                 border_radius=radius + spread - inset)
            if len(self._shadow_cache) > 160:   # ältesten Eintrag verwerfen
                self._shadow_cache.pop(next(iter(self._shadow_cache)))
            self._shadow_cache[key] = surf
        self.screen.blit(surf, (x - spread, y - spread + dy))

    def _panel_surface(self, w, h, radius, top, bottom, border, border_w):
        key = (w, h, radius, top, bottom, border, border_w)
        surf = self._panel_cache.get(key)
        if surf is not None:
            return surf
        base = pygame.Surface((w, h), pygame.SRCALPHA)
        for y in range(h):
            pygame.draw.line(base, _lerp_color(top, bottom, y / max(1, h)), (0, y), (w, y))
        mask = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, w, h), border_radius=radius)
        base.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        # oberer Glanz
        hi = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.line(hi, (*PANEL_HI, 90), (radius, 1), (w - radius, 1))
        base.blit(hi, (0, 0))
        if border_w > 0:
            pygame.draw.rect(base, border, (0, 0, w, h), border_w, border_radius=radius)
        if len(self._panel_cache) > 320:        # ältesten Eintrag verwerfen
            self._panel_cache.pop(next(iter(self._panel_cache)))
        self._panel_cache[key] = base
        return base

    def _panel(self, rect, radius=14, top=PANEL_FILL2, bottom=PANEL_FILL,
               border=PANEL_LINE, border_w=2, shadow=True):
        """Modernes Glas-Panel mit Schatten, Gradient & Rahmen"""
        x, y, w, h = rect
        if shadow:
            self._shadow((x, y, w, h), radius=radius)
        surf = self._panel_surface(int(w), int(h), radius, top, bottom, border, border_w)
        self.screen.blit(surf, (x, y))

    def _text(self, text, font, color, x, y, center=False, right=False, shadow=False):
        if shadow:
            sh = font.render(text, True, (0, 0, 0))
            sh.set_alpha(150)
        surf = font.render(text, True, color)
        if center:
            x -= surf.get_width() // 2
        elif right:
            x -= surf.get_width()
        if shadow:
            self.screen.blit(sh, (x + 1, y + 1))
        self.screen.blit(surf, (x, y))
        return surf.get_width()

    def _bar(self, x, y, w, h, ratio, col, bg=GREY_DARK, radius=6, glow=False):
        """Moderner Fortschrittsbalken mit Verlauf"""
        ratio = max(0.0, min(1.0, ratio))
        pygame.draw.rect(self.screen, bg, (x, y, w, h), border_radius=radius)
        fw = int(w * ratio)
        if fw > 0:
            # EIN Vollbreiten-Gradient cachen und nur den linken Teil blitten,
            # statt pro HP-Breite ein eigenes Surface zu cachen (vermeidet Cache-Flut).
            fill = self._panel_surface(w, h, min(radius, h // 2),
                                       _lighten(col, 0.3), _darken(col, 0.15),
                                       (0, 0, 0), 0)
            self.screen.blit(fill, (x, y), area=(0, 0, fw, h))
            # Glanzlinie
            pygame.draw.line(self.screen, _lighten(col, 0.5),
                             (x + 2, y + 2), (x + fw - 2, y + 2))
        pygame.draw.rect(self.screen, _lighten(bg, 0.3), (x, y, w, h), 1, border_radius=radius)

    def _chip(self, text, font, x, y, text_col=INK, fill=(0, 0, 0, 110),
              pad_x=10, pad_y=5, border=None):
        """Kleine abgerundete 'Pille' für Stat-Anzeigen"""
        tw = font.size(text)[0]
        th = font.get_height()
        w = tw + pad_x * 2
        h = th + pad_y * 2
        chip = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(chip, fill, (0, 0, w, h), border_radius=h // 2)
        if border:
            pygame.draw.rect(chip, border, (0, 0, w, h), 1, border_radius=h // 2)
        self.screen.blit(chip, (x, y))
        self._text(text, font, text_col, x + pad_x, y + pad_y)
        return w, h

    # ═══════════════════════════════════════════════
    # STATUSLEISTE
    # ═══════════════════════════════════════════════

    # Status -> (Sprite-Name in assets/status, Emoji-Fallback)
    _STATUS_ART = {
        "block": ("block", "🛡"), "strength": ("strength", "💪"),
        "burn": ("burn", "🔥"), "poison": ("poison", "☠️"),
        "regen": ("regen", "🌿"), "thorns": (None, "🌵"),
        "rage": ("rage", "😤"), "focus": ("focus", "🎯"),
        "vulnerable": ("vulnerable", "💔"), "weak": ("weak", "😵"),
        "frost": ("frost", "❄️"), "marked": ("marked", "🩸"),
        "stun": ("stun", "💫"), "doom": ("doom", "💀"),
        "mult": (None, "✖️"),
    }

    def _sb_chip_w(self, key, label):
        has_icon = self._STATUS_ART.get(key, (None, None))[0] or self._STATUS_ART.get(key, (None, None))[1]
        lw = self.font_tiny.size(label)[0] if label else 0
        return 14 + (18 if has_icon else 0) + (3 if (has_icon and lw) else 0) + lw

    def _sb_chip(self, x, y, key, label, color, fill):
        sprite, emoji = self._STATUS_ART.get(key, (None, "?"))
        w = self._sb_chip_w(key, label)
        h = self.font_tiny.get_height() + 8
        chip = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(chip, fill, (0, 0, w, h), border_radius=h // 2)
        pygame.draw.rect(chip, (*color, 110), (0, 0, w, h), 1, border_radius=h // 2)
        self.screen.blit(chip, (x, y))
        cx = x + 7
        icon = assets.scaled("status", sprite, 16, 16) if sprite else None
        if icon:
            self.screen.blit(icon, (cx, y + h // 2 - 8)); cx += 21
        elif emoji:
            self._text(emoji, self.font_tiny, WHITE, cx, y + 4); cx += 21
        if label:
            self._text(label, self.font_tiny, color, cx, y + 4)
        return w, h

    def _sb_strip(self, items, xl, xr, ytop, align, hot, row_h=23):
        """Status-Chips in der Zone [xl,xr] umbrechen (links- oder rechtsbündig)."""
        measured = [(self._sb_chip_w(k, lbl), k, lbl, col, fill, desc)
                    for (k, lbl, col, fill, desc) in items]
        maxw = xr - xl
        rows, cur, curw = [], [], 0
        for m in measured:
            if cur and curw + m[0] + 5 > maxw:
                rows.append((cur, curw - 5)); cur, curw = [], 0
            cur.append(m); curw += m[0] + 5
        if cur:
            rows.append((cur, curw - 5))
        y = ytop
        for row, rw in rows:
            x = xl if align == "left" else max(xl, xr - rw)
            for w, k, lbl, col, fill, desc in row:
                self._sb_chip(x, y, k, lbl, col, fill)
                hot.append((pygame.Rect(x, y, w, h := self.font_tiny.get_height() + 8), desc))
                x += w + 5
            y += row_h

    def draw_status_bar(self, player, enemy, floor_num, turn_num):
        """Obere Leiste (zweistöckig): Ressourcen oben, Status-Zeilen unten.
        Status-Zonen sind begrenzt & brechen um -> laufen nie über (TODO #13)."""
        bar_h = 106
        strip = pygame.Surface((self.w, bar_h), pygame.SRCALPHA)
        pygame.draw.rect(strip, (*DARKER_BG, 240), (0, 0, self.w, bar_h))
        self.screen.blit(strip, (0, 0))
        pygame.draw.line(self.screen, _darken(ACCENT, 0.45), (0, bar_h), (self.w, bar_h), 2)
        pygame.draw.line(self.screen, (*ACCENT, 60), (0, 1), (self.w, 1), 1)

        self._buff_tip = None
        mx, my = self._mouse
        hot = []

        # ── Tier 1: HP / Energie / Gold (links) ──
        hp_ratio = player.hp / max(1, player.max_hp)
        hp_color = HP_GREEN if hp_ratio > 0.5 else (ORANGE if hp_ratio > 0.25 else HP_RED)
        bx, by, bw, bh = 14, 12, 210, 20
        self._bar(bx, by, bw, bh, hp_ratio, hp_color, radius=10)
        self._text(f"❤ {player.hp}/{player.max_hp}", self.font_small, WHITE,
                   bx + 10, by + 2, shadow=True)
        ex = bx + bw + 12
        ew, eh = self._chip(f"⚡ {player.energy}/{player.max_energy}", self.font_medium,
                            ex, 11, text_col=CYAN, fill=(20, 50, 70, 180))
        hot.append((pygame.Rect(ex, 11, ew, eh),
                    "⚡ Energie: zahlt das Spielen von Karten. Füllt sich jede Runde auf."))
        gx = ex + ew + 8
        gw, gh = self._chip(f"💰 {player.gold}", self.font_medium, gx, 11,
                            text_col=ACCENT, fill=(60, 45, 10, 180))
        hot.append((pygame.Rect(gx, 11, gw, gh),
                    "💰 Gold: Währung für Shop, Glücksspiel und manche Karten."))

        # ── Tier 1: Etage/Runde (Mitte) ──
        center_txt = f"ETAGE {floor_num}  ·  RUNDE {turn_num}"
        tw = self.font_title.size(center_txt)[0]
        pill = pygame.Surface((tw + 32, 32), pygame.SRCALPHA)
        pygame.draw.rect(pill, (*PANEL_FILL, 235), (0, 0, tw + 32, 32), border_radius=16)
        pygame.draw.rect(pill, _darken(ACCENT, 0.3), (0, 0, tw + 32, 32), 1, border_radius=16)
        self.screen.blit(pill, (self.w // 2 - (tw + 32) // 2, 9))
        self._text(center_txt, self.font_title, ACCENT, self.w // 2, 13, center=True)

        # ── Tier 1: Gegner-Name + HP (rechts) ──
        ebw = 270
        ebx = self.w - 16 - ebw
        if enemy and enemy.is_alive():
            if enemy.is_boss:
                ncol = (255, 90, 90); prefix = "👑 "
            elif enemy.is_elite:
                ncol = ACCENT_SOFT; prefix = "⭐ "
            else:
                ncol = _lighten(enemy.color, 0.4); prefix = ""
            self._text(prefix + enemy.name, self.font_small, ncol, self.w - 16, 4,
                       right=True, shadow=True)
            self._bar(ebx, 24, ebw, 18, enemy.hp / max(1, enemy.max_hp), HP_RED, radius=8)
            self._text(f"{enemy.hp}/{enemy.max_hp}", self.font_tiny, WHITE,
                       ebx + ebw // 2, 25, center=True)

        # ── Tier 2: Spieler-Status (linke Zone, umbrechend) ──
        pit = []
        if player.block > 0:
            pit.append(("block", str(player.block), CYAN, (*BLUE_DARK, 160),
                        "Block: absorbiert eingehenden Schaden. Bleibt, bis er aufgebraucht ist."))
        if player.strength != 0:
            neg = player.strength < 0
            pit.append(("strength", f"{player.strength:+d}", (HP_RED if neg else ORANGE),
                        ((60, 12, 12, 170) if neg else (60, 35, 10, 170)),
                        f"Stärke: {player.strength:+d} Schaden auf jeden Angriff."
                        + (" Verspotten hat dich geschwächt!" if neg else "")))
        if player.burn > 0:
            pit.append(("burn", str(player.burn), ORANGE, (60, 25, 10, 170),
                        f"Brennen: −{player.burn} HP zu Rundenbeginn (sinkt um 1)."))
        if player.poison > 0:
            pit.append(("poison", str(player.poison), GREEN, (15, 50, 20, 170),
                        f"Gift: −{player.poison} HP zu Rundenbeginn, ignoriert Block (sinkt um 1)."))
        if player.regen > 0:
            pit.append(("regen", str(player.regen), GREEN, (15, 50, 30, 170),
                        f"Regeneration: +{player.regen} HP zu Rundenbeginn (sinkt um 1)."))
        if player.thorns > 0:
            pit.append(("thorns", str(player.thorns), ORANGE, (50, 40, 10, 170),
                        f"Dornen: reflektiert {player.thorns} Schaden je Gegnertreffer."))
        if getattr(player, "rage", 0) > 0:
            pit.append(("rage", str(player.rage), RED, (60, 15, 15, 170),
                        f"Wut: +{player.rage} Stärke zu Beginn jeder Runde."))
        if getattr(player, "focus", 0) > 0:
            pit.append(("focus", str(player.focus), ACCENT, (60, 45, 10, 170),
                        f"Fokus: deine nächste Angriffskarte macht +{player.focus} Schaden."))
        if getattr(player, "vulnerable", 0) > 0:
            pit.append(("vulnerable", str(player.vulnerable), HP_RED, (60, 12, 12, 170),
                        f"Verwundbar: du nimmst +50% Schaden ({player.vulnerable} Runden)."))
        if getattr(player, "mult", 1.0) != 1.0:
            pit.append(("mult", f"{player.mult:g}", PURPLE, (40, 20, 55, 170),
                        f"Multiplikator: Mult-Karten machen ×{player.mult:g} Schaden."))
        self._sb_strip(pit, 14, self.w // 2 - 160, 44, "left", hot)

        # ── Tier 2: Gegner-Status + Absicht (rechte Zone, rechtsbündig) ──
        if enemy and enemy.is_alive():
            eit = []
            if getattr(enemy, "block", 0) > 0:
                eit.append(("block", str(enemy.block), CYAN, (*BLUE_DARK, 160),
                            "Block: absorbiert deinen Schaden."))
            if enemy.burn > 0:
                eit.append(("burn", str(enemy.burn), ORANGE, (60, 25, 10, 170),
                            f"Brennen: −{enemy.burn} HP/Runde."))
            if enemy.poison > 0:
                eit.append(("poison", str(enemy.poison), GREEN, (15, 50, 20, 170),
                            f"Gift: −{enemy.poison} HP/Runde, ignoriert Block."))
            if enemy.vulnerable > 0:
                eit.append(("vulnerable", str(enemy.vulnerable), RED, (60, 12, 12, 170),
                            f"Verwundbar: nimmt +50% Schaden ({enemy.vulnerable} Runden)."))
            if enemy.weakened > 0:
                eit.append(("weak", str(enemy.weakened), PURPLE, (40, 20, 55, 170),
                            f"Geschwächt: macht weniger Schaden ({enemy.weakened} Runden)."))
            if getattr(enemy, "frost", 0) > 0:
                eit.append(("frost", str(enemy.frost), CYAN, (15, 45, 55, 170),
                            f"Frost: halber Angriffsschaden ({enemy.frost} Runden)."))
            if getattr(enemy, "marked", 0) > 0:
                eit.append(("marked", str(enemy.marked), RED, (55, 15, 15, 170),
                            f"Markiert: nimmt +{enemy.marked} Schaden pro Treffer."))
            if getattr(enemy, "stunned", 0) > 0:
                eit.append(("stun", "", WHITE, (45, 45, 50, 170),
                            "Betäubt: überspringt seinen nächsten Zug."))
            if getattr(enemy, "doom", 0) > 0:
                eit.append(("doom", str(enemy.doom), CURSE_COL, (40, 15, 50, 170),
                            f"Verhängnis: in {enemy.doom} Runden ein massiver Selbstschlag."))
            self._sb_strip(eit, self.w // 2 + 160, self.w - 16, 44, "right", hot)
            # Absicht als kleine, rechtsbündige Zeile ganz unten
            intent = enemy.get_intent_text()
            arm = f"🛡{enemy.armor}  " if enemy.armor else ""
            self._text(arm + intent, self.font_tiny, INK_DIM, self.w - 16, 88,
                       right=True)

        for rect, desc in hot:
            if rect.collidepoint(mx, my):
                self._buff_tip = (desc, rect.x, rect.bottom + 6)
                break

    def draw_pending_buff_tooltip(self):
        """Zeichnet den (in draw_status_bar erkannten) Buff-Tooltip – zuletzt, über allem."""
        tip = getattr(self, "_buff_tip", None)
        if not tip:
            return
        text, x, y = tip
        lines = self._wrap_text(text, self.font_tiny, 250)
        w = max((self.font_tiny.size(l)[0] for l in lines), default=0) + 22
        h = 10 + len(lines) * 16 + 6
        x = min(x, self.w - w - 6)
        self._panel((x, y, w, h), radius=10, shadow=True)
        for i, l in enumerate(lines):
            self._text(l, self.font_tiny, INK, x + 11, y + 8 + i * 16)

    def draw_damage_preview(self, enemy, dmg):
        """Zeigt den voraussichtlichen Schaden als helles Geist-Segment auf der Gegner-HP-Leiste"""
        x = self.w - 286
        bx, by, bh = x, 24, 18
        bw = 270
        mx = max(1, enemy.max_hp)
        now = enemy.hp / mx
        after = max(0, enemy.hp - dmg) / mx
        x1 = bx + int(bw * after)
        x2 = bx + int(bw * now)
        if x2 > x1:
            pulse = 0.5 + 0.5 * math.sin(self._anim_t * 8)
            seg = pygame.Surface((x2 - x1, bh), pygame.SRCALPHA)
            seg.fill((255, 255, 255, int(70 + 90 * pulse)))
            self.screen.blit(seg, (x1, by))
            pygame.draw.rect(self.screen, (255, 180, 160), (x1, by, x2 - x1, bh), 1)

    def draw_player_hp_preview(self, player, heal, incoming):
        """Vorschau auf der eigenen HP-Leiste: Heilung (grün vor) + Schaden (rot hinten)."""
        bx, by, bw, bh = 14, 12, 210, 20
        mx = max(1, player.max_hp)
        hp = player.hp

        def xat(v):
            return bx + int(bw * max(0, min(mx, v)) / mx)

        pulse = 0.5 + 0.5 * math.sin(self._anim_t * 8)
        rx = bx + bw - 4

        # Eingehender Schaden: rotes Verlust-Segment am rechten Ende der Füllung
        if incoming > 0:
            x1, x2 = xat(hp - incoming), xat(hp)
            if x2 > x1:
                seg = pygame.Surface((x2 - x1, bh), pygame.SRCALPHA)
                seg.fill((255, 50, 50, int(120 + 90 * pulse)))
                self.screen.blit(seg, (x1, by))
                pygame.draw.rect(self.screen, (255, 170, 170), (x1, by, x2 - x1, bh), 1)
            self._text(f"-{incoming}", self.font_tiny, (255, 215, 215), rx, by + 4,
                       right=True, shadow=True)
            rx -= self.font_tiny.size(f"-{incoming}")[0] + 8

        # Heilung: grünes Gewinn-Segment hinter der aktuellen Füllung
        if heal > 0:
            x1, x2 = xat(hp), xat(hp + heal)
            if x2 > x1:
                seg = pygame.Surface((x2 - x1, bh), pygame.SRCALPHA)
                seg.fill((90, 230, 120, int(120 + 90 * pulse)))
                self.screen.blit(seg, (x1, by))
                pygame.draw.rect(self.screen, (190, 255, 200), (x1, by, x2 - x1, bh), 1)
            self._text(f"+{heal}", self.font_tiny, (200, 255, 210), rx, by + 4,
                       right=True, shadow=True)

    # ═══════════════════════════════════════════════
    # RELIKTE
    # ═══════════════════════════════════════════════

    def draw_relic_bar(self, player, x, y):
        """Relikt-Leiste: füllt Spalten von oben nach unten, dann weitere Spalten
        nach rechts (max. 3, bleibt links vom Avatar). Bei Überlauf '+N'.
        Tooltip wird NICHT hier gezeichnet, sondern verzögert (über den Karten)."""
        self._relic_tip = None
        if not player.relics:
            return
        mx, my = self._mouse
        chip, gap = 32, 6
        step = chip + gap
        bottom = 612                       # nicht in die Hand-Karten laufen
        max_cols = 3
        rows = max(1, (bottom - y) // step)
        capacity = rows * max_cols
        relics = player.relics
        overflow = len(relics) - capacity
        shown = relics[:capacity - 1] if overflow > 0 else relics
        hovered = None
        for i, relic in enumerate(shown):
            col, row = divmod(i, rows)
            rx = x + col * step
            ry = y + row * step
            rect = pygame.Rect(rx, ry, chip, chip)
            hot = rect.collidepoint(mx, my)
            col_bg = (50, 40, 20) if hot else (34, 28, 50)
            border = ACCENT if hot else PANEL_LINE
            pygame.draw.rect(self.screen, col_bg, rect, border_radius=9)
            pygame.draw.rect(self.screen, border, rect, 2, border_radius=9)
            spr = assets.fit("relics", relic.get("id"), chip - 6, chip - 6)
            if spr:
                self.screen.blit(spr, (rx + chip // 2 - spr.get_width() // 2,
                                       ry + chip // 2 - spr.get_height() // 2))
            else:
                em = self.font_medium.render(relic["emoji"], True, WHITE)
                self.screen.blit(em, (rx + chip // 2 - em.get_width() // 2,
                                      ry + chip // 2 - em.get_height() // 2))
            if hot:
                hovered = relic
        if overflow > 0:
            # '+N'-Kachel als letztes Feld
            i = len(shown)
            col, row = divmod(i, rows)
            rx, ry = x + col * step, y + row * step
            rect = pygame.Rect(rx, ry, chip, chip)
            pygame.draw.rect(self.screen, (44, 36, 60), rect, border_radius=9)
            pygame.draw.rect(self.screen, PANEL_LINE, rect, 2, border_radius=9)
            self._text(f"+{overflow + 1}", self.font_tiny, ACCENT_SOFT,
                       rx + chip // 2, ry + chip // 2 - 7, center=True)
        if hovered:
            # Position merken; tatsächlich gezeichnet wird in
            # draw_pending_relic_tooltip() NACH den Karten (TODO #6).
            self._relic_tip = (hovered, x + max_cols * step + 6, my)

    def draw_pending_relic_tooltip(self):
        """Zeichnet den Relikt-Tooltip zuletzt, damit er über den Karten liegt."""
        tip = getattr(self, "_relic_tip", None)
        if tip:
            self._relic_tooltip(*tip)

    def _relic_tooltip(self, relic, x, y):
        title = f"{relic['emoji']} {relic['name']}"
        lines = self._wrap_text(relic["desc"], self.font_tiny, 200)
        w = max(self.font_small.size(title)[0],
                max((self.font_tiny.size(l)[0] for l in lines), default=0)) + 24
        h = 30 + len(lines) * 16 + 8
        y = min(y, self.h - h - 6)
        self._panel((x, y, w, h), radius=10, shadow=True)
        self._text(title, self.font_small, ACCENT_SOFT, x + 12, y + 8)
        for i, l in enumerate(lines):
            self._text(l, self.font_tiny, INK_DIM, x + 12, y + 30 + i * 16)

    # ═══════════════════════════════════════════════
    # COMBO
    # ═══════════════════════════════════════════════

    def draw_combo_badge(self, count, ctype, flash):
        """Auffälliges Combo-Abzeichen"""
        label = {"attack": "ANGRIFF", "defense": "VERTEIDIGUNG", "special": "SPECIAL"}.get(ctype, "")
        col = {"attack": RED, "defense": BLUE, "special": PURPLE}.get(ctype, ACCENT)
        txt = f"🔥 COMBO ×{count}  ·  {label}"
        f = self.font_medium
        tw = f.size(txt)[0]
        w = int((tw + 36))
        h = 34
        x = self.w // 2 - w // 2
        y = 150  # oben mittig, unter der Etagen-Pille
        glow_a = int(60 + 120 * flash)
        glow = pygame.Surface((w + 20, h + 20), pygame.SRCALPHA)
        pygame.draw.rect(glow, (*col, glow_a), (0, 0, w + 20, h + 20), border_radius=20)
        self.screen.blit(glow, (x - 10, y - 10))
        self._panel((x, y, w, h), radius=17, top=_darken(col, 0.2), bottom=_darken(col, 0.45),
                    border=_lighten(col, 0.3), shadow=False)
        self._text(txt, f, WHITE, self.w // 2, y + 7, center=True, shadow=True)

    # ═══════════════════════════════════════════════
    # GEGNER-DARSTELLUNG
    # ═══════════════════════════════════════════════

    def draw_enemy(self, enemy, x, y, width, height):
        if not enemy or not enemy.is_alive():
            return
        t = self._anim_t
        body_x = x + width // 2
        wobble = int(3 * math.sin(t * 2))
        body_y = y + height // 2 + wobble

        # Boden-Plattform (Ellipse mit Verlauf)
        plat = pygame.Surface((200, 60), pygame.SRCALPHA)
        for i in range(6):
            a = 60 - i * 9
            pygame.draw.ellipse(plat, (0, 0, 0, max(0, a)),
                                (i * 4, 30 + i * 2, 200 - i * 8, 28 - i * 3))
        self.screen.blit(plat, (body_x - 100, y + height - 36))

        # Aura für Boss/Elite
        if enemy.is_boss or enemy.is_elite:
            pulse = abs(math.sin(t * 1.5)) * 0.4 + 0.6
            aura_col = (220, 70, 70) if enemy.is_boss else ACCENT
            aura = pygame.Surface((width, height), pygame.SRCALPHA)
            pygame.draw.circle(aura, (*aura_col, int(50 * pulse)),
                               (width // 2, height // 2), int(70 * pulse) + 30)
            self.screen.blit(aura, (x, y))

        # Sprite (falls vorhanden) – sonst prozedurale Figur
        sprite_h = int(min(height - 24, 210) * (1.15 if (enemy.is_boss or enemy.is_elite) else 1.0))
        spr = assets.by_height("enemies", enemy.asset, sprite_h)
        if spr:
            sx = body_x - spr.get_width() // 2
            sy = (y + height - 24) - spr.get_height() + wobble
            self.screen.blit(spr, (sx, sy))
        elif enemy.is_boss:
            pygame.draw.circle(self.screen, _darken(enemy.color, 0.2), (body_x, body_y), 56)
            pygame.draw.circle(self.screen, enemy.color, (body_x, body_y), 52)
            pygame.draw.circle(self.screen, _lighten(enemy.color, 0.3), (body_x, body_y), 52, 3)
            crown_pts = [(body_x - 30, body_y - 52), (body_x - 18, body_y - 70),
                         (body_x, body_y - 58), (body_x + 18, body_y - 70),
                         (body_x + 30, body_y - 52)]
            pygame.draw.polygon(self.screen, ACCENT, crown_pts)
            pygame.draw.polygon(self.screen, _darken(ACCENT, 0.3), crown_pts, 2)
            pygame.draw.circle(self.screen, RED, (body_x - 16, body_y - 8), 8)
            pygame.draw.circle(self.screen, RED, (body_x + 16, body_y - 8), 8)
            pygame.draw.circle(self.screen, WHITE, (body_x - 16, body_y - 8), 8, 1)
            pygame.draw.circle(self.screen, WHITE, (body_x + 16, body_y - 8), 8, 1)
            pygame.draw.arc(self.screen, WHITE, (body_x - 22, body_y + 6, 44, 26),
                            math.pi, 2 * math.pi, 3)
        else:
            bc = enemy.color
            pygame.draw.ellipse(self.screen, _darken(bc, 0.15), (body_x - 36, body_y - 38, 72, 82))
            pygame.draw.ellipse(self.screen, bc, (body_x - 34, body_y - 40, 68, 80))
            pygame.draw.ellipse(self.screen, _lighten(bc, 0.35), (body_x - 34, body_y - 40, 68, 80), 2)
            pygame.draw.circle(self.screen, bc, (body_x, body_y - 50), 24)
            pygame.draw.circle(self.screen, _lighten(bc, 0.35), (body_x, body_y - 50), 24, 2)
            # Augen
            for ex in (-8, 8):
                pygame.draw.circle(self.screen, WHITE, (body_x + ex, body_y - 52), 6)
                pygame.draw.circle(self.screen, BLACK, (body_x + ex, body_y - 51), 3)
            # Arme
            pygame.draw.line(self.screen, _darken(bc, 0.1),
                             (body_x - 32, body_y - 18), (body_x - 54, body_y + wobble * 2), 7)
            pygame.draw.line(self.screen, _darken(bc, 0.1),
                             (body_x + 32, body_y - 18), (body_x + 54, body_y + wobble * 2), 7)

        # Name-Plakette unter dem Gegner
        name = enemy.name
        nf = self.font_small
        nw = nf.size(name)[0]
        plate = pygame.Surface((nw + 24, 26), pygame.SRCALPHA)
        pygame.draw.rect(plate, (*DARKER_BG, 220), (0, 0, nw + 24, 26), border_radius=13)
        ncol = ACCENT if (enemy.is_boss or enemy.is_elite) else INK
        pygame.draw.rect(plate, _darken(ncol, 0.4), (0, 0, nw + 24, 26), 1, border_radius=13)
        self.screen.blit(plate, (body_x - (nw + 24) // 2, y + height - 18))
        self._text(name, nf, ncol, body_x, y + height - 14, center=True)

        # (Gegner-Status-Chips stehen jetzt in der oberen Leiste, mit Hover-Erklärung.)

        # Slot-Boss: zuletzt gedrehte Symbole über dem Boss anzeigen (kleiner Automat)
        last = getattr(enemy, "last_slot", None)
        if last:
            import entities as _ent
            cw, n = 46, len(last)
            pw = n * cw + 16
            pcx = body_x - pw // 2
            pcy = body_y - 118
            panel = pygame.Surface((pw, 54), pygame.SRCALPHA)
            pygame.draw.rect(panel, (30, 22, 10, 230), (0, 0, pw, 54), border_radius=10)
            pygame.draw.rect(panel, GOLD, (0, 0, pw, 54), 2, border_radius=10)
            self.screen.blit(panel, (pcx, pcy))
            for i, sym in enumerate(last):
                em = _ent.SLOT_BOSS_EMOJI.get(sym, "?")
                self._text(em, self.font_large, WHITE, pcx + 8 + i * cw + cw // 2,
                           pcy + 8, center=True)

        # Block-Schild: verankert am Sprite-Fuß (mit Wobble, damit es mitschwingt)
        if getattr(enemy, "block", 0) > 0:
            self._block_badge(body_x, y + height - 54 + wobble, enemy.block)

    def _block_badge(self, cx, cy, amount):
        """Blaues Schild mit Block-Zahl"""
        pts = [(cx, cy - 16), (cx + 15, cy - 9), (cx + 15, cy + 4),
               (cx, cy + 16), (cx - 15, cy + 4), (cx - 15, cy - 9)]
        pygame.draw.polygon(self.screen, (40, 90, 160), pts)
        pygame.draw.polygon(self.screen, (120, 180, 255), pts, 2)
        bt = self.font_small.render(str(amount), True, WHITE)
        self.screen.blit(bt, (cx - bt.get_width() // 2, cy - bt.get_height() // 2))

    def draw_player_side(self, player, x, y, width, height):
        """Spieler-Avatar (links) – analog zur Gegner-Darstellung."""
        t = self._anim_t
        body_x = x + width // 2
        wobble = int(2 * math.sin(t * 1.8))
        # Plattform
        plat = pygame.Surface((200, 60), pygame.SRCALPHA)
        for i in range(6):
            a = 60 - i * 9
            pygame.draw.ellipse(plat, (0, 0, 0, max(0, a)),
                                (i * 4, 30 + i * 2, 200 - i * 8, 28 - i * 3))
        self.screen.blit(plat, (body_x - 100, y + height - 36))

        # Avatar = Klassen-Portrait (falls Klasse gewählt), sonst generischer Held
        cid = getattr(player, "class_id", None)
        h = min(height - 24, 210)
        spr = assets.by_height("ui", f"class_{cid}", h) if cid else None
        if spr is None:
            spr = assets.by_height("ui", "player_avatar", h)
        if spr:
            sx = body_x - spr.get_width() // 2
            sy = (y + height - 24) - spr.get_height() + wobble
            self.screen.blit(spr, (sx, sy))

        # Namensplakette "DU"
        nw = self.font_small.size("DU")[0]
        plate = pygame.Surface((nw + 24, 26), pygame.SRCALPHA)
        pygame.draw.rect(plate, (*DARKER_BG, 220), (0, 0, nw + 24, 26), border_radius=13)
        pygame.draw.rect(plate, _darken(CYAN, 0.4), (0, 0, nw + 24, 26), 1, border_radius=13)
        self.screen.blit(plate, (body_x - (nw + 24) // 2, y + height - 18))
        self._text("DU", self.font_small, CYAN, body_x, y + height - 14, center=True)

        # Block-Schild auch beim Spieler sichtbar (mit Wobble verankert)
        if player.block > 0:
            self._block_badge(body_x, y + height - 54 + wobble, player.block)

    # ═══════════════════════════════════════════════
    # HANDKARTEN
    # ═══════════════════════════════════════════════

    def draw_hand(self, hand, selected_card=None, hovered_idx=None):
        if not hand:
            return []
        card_w, card_h = 130, 178
        gap = 8
        # Bei voller Hand etwas zusammenrücken, damit alles passt
        total_w = len(hand) * (card_w + gap)
        if total_w > self.w - 40:
            gap = max(-18, (self.w - 40 - len(hand) * card_w) // max(1, len(hand)))
            total_w = len(hand) * (card_w + gap)
        start_x = self.w // 2 - total_w // 2
        card_y = self.h - card_h - 6
        # zuerst nicht-gehoverte, dann gehoverte (oben drauf)
        order = [i for i in range(len(hand)) if i != hovered_idx]
        if hovered_idx is not None and hovered_idx < len(hand):
            order.append(hovered_idx)
        rects = [None] * len(hand)
        for i in range(len(hand)):
            cx = start_x + i * (card_w + gap)
            rects[i] = pygame.Rect(cx, card_y, card_w, card_h)
        for i in order:
            card = hand[i]
            active = (hovered_idx == i) or (selected_card == card)
            cx = start_x + i * (card_w + gap)
            if active:
                # Aktive Karte deutlich vergrößern (besser lesbar, TODO #7).
                # Inhalt skaliert automatisch mit der Höhe (scale = h/178).
                f = 1.4
                w2, h2 = int(card_w * f), int(card_h * f)
                lift = 30
                rx = cx + card_w // 2 - w2 // 2
                rx = max(6, min(self.w - w2 - 6, rx))        # im Bild halten
                ry = card_y + card_h - h2 - lift
                rect = pygame.Rect(rx, ry, w2, h2)
            else:
                rect = pygame.Rect(cx, card_y, card_w, card_h)
            rects[i] = rect
            self._draw_card(card, rect, selected=(selected_card == card),
                            hovered=(hovered_idx == i))
        return rects

    def _draw_card(self, card, rect, selected=False, hovered=False):
        x, y, w, h = rect
        rarity_col = card.get_rarity_color()
        active = selected or hovered

        # Schatten
        self._shadow((x, y, w, h), radius=12, spread=8,
                     alpha=150 if active else 110, dy=6 if active else 4)

        # Seltenheits-Rahmen-Sprite (falls vorhanden) – ersetzt den Procedural-Rand
        frame = assets.scaled("frames", card.rarity, w, h)

        # Karten-Korpus (dunkler Verlauf, leicht in Kartenfarbe getönt)
        tint_top = _lerp_color(CARD_BG, card.color, 0.16)
        tint_bot = _darken(CARD_BG, 0.25)
        body = self._panel_surface(w, h, 12, tint_top, tint_bot,
                                   rarity_col if active else CARD_BORDER,
                                   0 if frame else 2)
        self.screen.blit(body, (x, y))

        if active:
            glow = pygame.Surface((w + 12, h + 12), pygame.SRCALPHA)
            pygame.draw.rect(glow, (*rarity_col, 70), (0, 0, w + 12, h + 12), 4, border_radius=14)
            self.screen.blit(glow, (x - 6, y - 6))

        if frame:
            self.screen.blit(frame, (x, y))
            # Dunkles Lese-Panel hinter dem Text -> Text bleibt trotz Rahmen lesbar
            ins = max(9, int(w * 0.085))
            inner = pygame.Surface((w - 2 * ins, h - 2 * ins), pygame.SRCALPHA)
            pygame.draw.rect(inner, (10, 8, 16, 200), (0, 0, w - 2 * ins, h - 2 * ins), border_radius=8)
            self.screen.blit(inner, (x + ins, y + ins))
        else:
            pygame.draw.rect(self.screen, card.color, (x + 8, y + 7, w - 16, 5), border_radius=3)

        pad = max(12, int(w * 0.11))   # Text-Innenabstand
        scale = h / 178.0              # Layout skaliert mit Kartenhöhe

        # Kostenbadge
        cost_col = CYAN if card.cost == 0 else ACCENT
        cbx, cby, cr = x + pad + 6, int(y + 30 * scale), 16
        pygame.draw.circle(self.screen, _darken(cost_col, 0.55), (cbx, cby), cr)
        pygame.draw.circle(self.screen, cost_col, (cbx, cby), cr, 2)
        ct = self.font_medium.render(str(card.cost), True, WHITE)
        self.screen.blit(ct, (cbx - ct.get_width() // 2, cby - ct.get_height() // 2))

        # Effekt-Icon oben rechts (Sprite); Fallback aufs Typ-Emoji
        isz = max(18, int(28 * scale))
        icon = assets.scaled("cards", card.get_effect_icon(), isz, isz)
        if icon:
            self.screen.blit(icon, (x + w - pad - isz + 4, int(y + 12 * scale)))
        else:
            self._text(card.get_type_icon(), self.font_small, _lighten(card.color, 0.3),
                       x + w - pad, int(y + 22 * scale), right=True, shadow=True)

        # Name (mit Schatten für Lesbarkeit)
        name_lines = self._wrap_text(card.name, self.font_small, w - 2 * pad)
        for li, line in enumerate(name_lines[:2]):
            self._text(line, self.font_small, INK, x + pad, int(y + 46 * scale) + li * 17, shadow=True)

        # Trennlinie
        dvy = int(y + 80 * scale)
        pygame.draw.line(self.screen, (*ACCENT_SOFT, 70), (x + pad, dvy), (x + w - pad, dvy))

        # Wert + Schatten
        vy = int(y + 84 * scale)
        if card.damage > 0:
            self._text(f"⚔ {card.damage}", self.font_medium, _lighten(RED, 0.4), x + w // 2, vy, center=True, shadow=True)
        elif card.block > 0:
            self._text(f"🛡 {card.block}", self.font_medium, _lighten(BLUE, 0.4), x + w // 2, vy, center=True, shadow=True)
        elif card.heal > 0:
            self._text(f"💚 {card.heal}", self.font_medium, _lighten(GREEN, 0.4), x + w // 2, vy, center=True, shadow=True)
        else:
            icon = "💀" if card.type == "curse" else "✨"
            self._text(icon, self.font_medium, _lighten(PURPLE, 0.3), x + w // 2, vy, center=True, shadow=True)

        # Marker: exhaust
        if getattr(card, "exhaust", False):
            self._text("♻", self.font_small, ORANGE, x + w - pad, int(y + 64 * scale), right=True, shadow=True)

        # Beschreibung: eigener dunkler Kasten + heller Text -> gut lesbar
        ty = int(y + 110 * scale)
        tb = pygame.Rect(x + pad - 4, ty - 3, w - 2 * pad + 8, (y + h - 8) - ty + 6)
        box = pygame.Surface((tb.w, tb.h), pygame.SRCALPHA)
        pygame.draw.rect(box, (4, 3, 8, 225), (0, 0, tb.w, tb.h), border_radius=6)
        self.screen.blit(box, (tb.x, tb.y))
        self._draw_fitted_tooltip(card.tooltip, x + pad, ty, w - 2 * pad, (y + h - 10) - ty)

    def _draw_fitted_tooltip(self, text, x, y, w, h):
        """Beschreibungstext: größte passende Schrift, hell + Schatten."""
        candidates = [(self.font_small, 16), (self.font_tiny, 14),
                      (self._font_micro, 12), (self._font_nano, 10)]
        col = (232, 234, 244)
        font, line_h, lines = candidates[-1][0], candidates[-1][1], None
        for f, lh in candidates:
            wl = self._wrap_text(text, f, w)
            if len(wl) * lh <= h:
                font, line_h, lines = f, lh, wl
                break
        if lines is None:
            lines = self._wrap_text(text, font, w)[: max(1, h // line_h)]
        for li, line in enumerate(lines):
            self._text(line, font, col, x, y + li * line_h, shadow=True)

    def _wrap_text(self, text, font, max_width):
        words = text.split()
        lines, current = [], ""
        for word in words:
            test = current + (" " if current else "") + word
            if font.size(test)[0] <= max_width:
                current = test
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines

    # ═══════════════════════════════════════════════
    # KAMPF-LOG
    # ═══════════════════════════════════════════════

    def draw_combat_log(self, log_entries, x, y, w, h, scroll=0):
        # Casino-Look: dunkler Filz-Korpus + Messing-Doppelrahmen + Gold-Header
        felt = self._panel_surface(w, h, 12, (26, 34, 28), (14, 20, 16),
                                   GOLD_DARK, 2)
        self.screen.blit(felt, (x, y))
        pygame.draw.rect(self.screen, (*GOLD, 60), (x + 3, y + 3, w - 6, h - 6),
                         1, border_radius=10)
        # Gold-Header-Band
        head = pygame.Surface((w - 8, 22), pygame.SRCALPHA)
        pygame.draw.rect(head, (*GOLD_DARK, 235), (0, 0, w - 8, 22),
                         border_top_left_radius=9, border_top_right_radius=9)
        self.screen.blit(head, (x + 4, y + 4))

        max_lines = (h - 32) // 15
        newest_idx = len(log_entries) - 1
        # Lange Einträge umbrechen (mit Rand), statt überlaufen zu lassen.
        text_w = w - 26
        wrapped = []   # (zeile, gehört-zum-neuesten-eintrag)
        for ei, entry in enumerate(log_entries):
            parts = self._wrap_text(entry, self.font_tiny, text_w) or [""]
            for p in parts:
                wrapped.append((p, ei == newest_idx))
        total = len(wrapped)
        end = max(max_lines, total - scroll)
        view = wrapped[max(0, end - max_lines):end]

        old_clip = self.screen.get_clip()
        self.screen.set_clip(pygame.Rect(x, y, w, h))

        hdr = "📜 KAMPFLOG  ·  Mausrad scrollt" if total > max_lines else "📜 KAMPFLOG"
        self._text(hdr, self.font_tiny, (30, 22, 6), x + 12, y + 7)
        if scroll > 0:
            self._text("▲ älter", self.font_tiny, (60, 44, 10), x + w - 58, y + 7)

        nv = len(view)
        for i, (line, is_newest) in enumerate(view):
            newest = is_newest and scroll == 0
            color = GOLD if newest else _lerp_color(INK_FAINT, INK, (i + 1) / max(1, nv))
            self._text(line, self.font_tiny, color, x + 12, y + 32 + i * 15)
        self.screen.set_clip(old_clip)

    # ═══════════════════════════════════════════════
    # BUTTONS
    # ═══════════════════════════════════════════════

    def draw_button(self, text, x, y, w, h, color=ACCENT, text_color=BLACK,
                    disabled=False, pulsing=False):
        rect = pygame.Rect(x, y, w, h)
        if disabled:
            self._panel((x, y, w, h), radius=11, top=_darken(GREY_DARK, 0.1),
                        bottom=_darken(GREY_DARK, 0.4), border=GREY_DARK, shadow=False)
            self._text(text, self.font_medium, GREY, x + w // 2, y + h // 2 - 11, center=True)
            return rect

        hovered = rect.collidepoint(self._mouse)
        lift = 2 if hovered else 0
        col = _lighten(color, 0.12) if hovered else color

        if pulsing or hovered:
            p = abs(math.sin(self._anim_t * 3)) if pulsing else 1.0
            ga = int((50 if hovered else 0) + 70 * p)
            if ga > 0:
                glow = pygame.Surface((w + 18, h + 18), pygame.SRCALPHA)
                pygame.draw.rect(glow, (*col, ga), (0, 0, w + 18, h + 18), border_radius=16)
                self.screen.blit(glow, (x - 9, y - 9 - lift))

        self._shadow((x, y - lift, w, h), radius=11, spread=7, alpha=120, dy=5)
        surf = self._panel_surface(w, h, 11, _lighten(col, 0.22), _darken(col, 0.12),
                                   _lighten(col, 0.4), 2)
        self.screen.blit(surf, (x, y - lift))
        # Text mit leichtem Schatten
        tsurf = self.font_medium.render(text, True, text_color)
        self.screen.blit(tsurf, (x + w // 2 - tsurf.get_width() // 2,
                                 y - lift + h // 2 - tsurf.get_height() // 2))
        return rect

    def draw_slot_button(self, x, y, w, h, pulsing=True):
        """Thematischer 'Slot drehen'-Knopf im Casino-Cabinet-Look."""
        rect = pygame.Rect(x, y, w, h)
        hovered = rect.collidepoint(self._mouse)
        lift = 2 if hovered else 0
        # Glühen
        p = abs(math.sin(self._anim_t * 3)) if pulsing else 1.0
        ga = int((60 if hovered else 0) + 80 * p)
        if ga > 0:
            glow = pygame.Surface((w + 22, h + 22), pygame.SRCALPHA)
            pygame.draw.rect(glow, (255, 200, 70, ga), (0, 0, w + 22, h + 22), border_radius=18)
            self.screen.blit(glow, (x - 11, y - 11 - lift))
        self._shadow((x, y - lift, w, h), radius=13, spread=8, alpha=140, dy=6)
        # Cabinet: dunkelroter Rahmen + Gold-Korpus
        yy = y - lift
        pygame.draw.rect(self.screen, (90, 20, 24), (x, yy, w, h), border_radius=13)
        body = self._panel_surface(w - 8, h - 8, 10, (255, 224, 120), (210, 150, 30),
                                   (255, 240, 180), 2)
        self.screen.blit(body, (x + 4, yy + 4))
        # kleines Reel-Fenster links
        rfx, rfy, rfw, rfh = x + 12, yy + h // 2 - 10, 20, 20
        pygame.draw.rect(self.screen, (40, 28, 12), (rfx, rfy, rfw, rfh), border_radius=4)
        self._text("🎰", self.font_small, WHITE, rfx + rfw // 2, rfy + 1, center=True)
        # Text
        self._text("SLOT DREHEN", self.font_title, (70, 30, 6), x + w // 2 + 8,
                   yy + h // 2 - 11, center=True, shadow=False)
        return rect

    # ═══════════════════════════════════════════════
    # OVERLAYS
    # ═══════════════════════════════════════════════

    def _dim(self, alpha=180):
        # Abdunkel-Overlays je Alpha cachen (sonst 3,8 MB Surface pro Frame).
        cache = self.__dict__.setdefault("_dim_cache", {})
        overlay = cache.get(alpha)
        if overlay is None:
            overlay = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, alpha))
            cache[alpha] = overlay
        self.screen.blit(overlay, (0, 0))

    def draw_damage_number(self, text, x, y, color=RED, offset=0):
        surf = self.font_title.render(text, True, color)
        self.screen.blit(surf, (x - surf.get_width() // 2, y - offset))

    # ═══════════════════════════════════════════════
    # BELOHNUNG
    # ═══════════════════════════════════════════════

    def draw_reward_screen(self, cards, gold_reward, player, relic=None):
        self._dim(180)
        pw, ph = 760, 540
        px, py = self.w // 2 - pw // 2, self.h // 2 - ph // 2
        self._panel((px, py, pw, ph), radius=18, border=ACCENT, border_w=3)

        self._text("⚔  SIEG!  ⚔", self.font_huge, ACCENT, self.w // 2, py + 20, center=True, shadow=True)
        self._text(f"💰 +{gold_reward} Gold erhalten", self.font_title, ACCENT_SOFT,
                   self.w // 2, py + 76, center=True)

        top = py + 116
        if relic:
            # Relikt-Banner
            bw = 420
            bx = self.w // 2 - bw // 2
            self._panel((bx, top, bw, 40), radius=12, top=(60, 48, 22), bottom=(40, 32, 14),
                        border=ACCENT, shadow=False)
            self._text(f"💠 Relikt: {relic['emoji']} {relic['name']}", self.font_small,
                       ACCENT_SOFT, self.w // 2, top + 11, center=True)
            top += 52

        self._text("Wähle eine Karte für dein Deck:", self.font_small, INK_DIM,
                   self.w // 2, top, center=True)

        card_rects = []
        card_w = 162
        spacing = 22
        total_w = len(cards) * card_w + (len(cards) - 1) * spacing
        cx_start = self.w // 2 - total_w // 2
        for i, card in enumerate(cards):
            cx = cx_start + i * (card_w + spacing)
            cy = top + 30
            hov = pygame.Rect(cx, cy, card_w, 210).collidepoint(self._mouse)
            rect = pygame.Rect(cx, cy - (8 if hov else 0), card_w, 210)
            card_rects.append(pygame.Rect(cx, cy, card_w, 210))
            self._draw_card(card, rect, hovered=hov)

        skip_rect = pygame.Rect(self.w // 2 - 90, py + ph - 58, 180, 42)
        self.draw_button("Überspringen", skip_rect.x, skip_rect.y, skip_rect.w, skip_rect.h,
                         color=GREY_DARK, text_color=WHITE)
        return card_rects, skip_rect

    def draw_relic_reward(self, relics, player, hovered_idx=None):
        """Relikt-Auswahl: 3 Relikte zur Wahl, je mit Icon, Name & Beschreibung."""
        self.draw_background()
        self._dim(180)
        pw, ph = 820, 460
        px, py = self.w // 2 - pw // 2, self.h // 2 - ph // 2
        self._panel((px, py, pw, ph), radius=18, border=ACCENT, border_w=3)

        self._text("💠  RELIKT WÄHLEN  💠", self.font_huge, ACCENT,
                   self.w // 2, py + 22, center=True, shadow=True)
        self._text("Wähle EIN Relikt für deinen Build:", self.font_small, INK_DIM,
                   self.w // 2, py + 78, center=True)

        rects = []
        n = len(relics)
        cw, ch = 230, 270
        spacing = 26
        total_w = n * cw + (n - 1) * spacing
        cx_start = self.w // 2 - total_w // 2
        cy = py + 112
        mx, my = self._mouse
        for i, relic in enumerate(relics):
            cx = cx_start + i * (cw + spacing)
            rect = pygame.Rect(cx, cy, cw, ch)
            hot = (hovered_idx == i) or rect.collidepoint(mx, my)
            self._panel((cx, cy - (6 if hot else 0), cw, ch), radius=14,
                        top=_lighten(PANEL_FILL2, 0.14) if hot else PANEL_FILL2,
                        bottom=PANEL_FILL,
                        border=ACCENT if hot else PANEL_LINE,
                        border_w=3 if hot else 2, shadow=hot)
            top = cy - (6 if hot else 0)
            # Icon
            spr = assets.fit("relics", relic.get("id"), 72, 72)
            if spr:
                self.screen.blit(spr, (cx + cw // 2 - spr.get_width() // 2, top + 16))
            else:
                self._text(relic.get("emoji", "💠"), self.font_huge, WHITE,
                           cx + cw // 2, top + 22, center=True)
            # Name
            self._text(relic["name"], self.font_medium, ACCENT_SOFT,
                       cx + cw // 2, top + 100, center=True)
            # Beschreibung (umgebrochen)
            desc = relic.get("desc", "")
            lines = self._wrap_text(desc, self.font_small, cw - 28)
            for j, line in enumerate(lines[:6]):
                self._text(line, self.font_small, INK,
                           cx + cw // 2, top + 134 + j * 22, center=True)
            rects.append(rect)
        return rects

    # ═══════════════════════════════════════════════
    # EVENT-SCREEN
    # ═══════════════════════════════════════════════

    def draw_event(self, event, resolved, result_text, hovered_idx):
        self.draw_background()
        pw, ph = 720, 580
        px, py = self.w // 2 - pw // 2, self.h // 2 - ph // 2
        self._panel((px, py, pw, ph), radius=18, border=PURPLE, border_w=3)

        art = assets.fit("events", event.get("asset"), 300, 150)
        if art:
            ax = self.w // 2 - art.get_width() // 2
            self._shadow((ax, py + 18, art.get_width(), art.get_height()), radius=8, spread=6)
            self.screen.blit(art, (ax, py + 18))
            pygame.draw.rect(self.screen, _darken(PURPLE, 0.2),
                             (ax, py + 18, art.get_width(), art.get_height()), 2, border_radius=6)
            title_y = py + 18 + art.get_height() + 6
        else:
            self._text(event["emoji"], self.font_huge, WHITE, self.w // 2, py + 22, center=True)
            title_y = py + 78
        self._text(event["title"], self.font_h1, _lighten(PURPLE, 0.4),
                   self.w // 2, title_y, center=True, shadow=True)

        # Beschreibung (umgebrochen, zentriert)
        desc_lines = self._wrap_text(event["text"], self.font_small, pw - 100)
        for i, line in enumerate(desc_lines):
            self._text(line, self.font_small, INK_DIM, self.w // 2, title_y + 42 + i * 20, center=True)

        option_rects = []
        continue_rect = None
        oy = title_y + 42 + len(desc_lines) * 20 + 18

        if not resolved:
            ow = pw - 120
            ox = self.w // 2 - ow // 2
            for i, opt in enumerate(event["options"]):
                rect = pygame.Rect(ox, oy, ow, 64)
                option_rects.append(rect)
                hot = (hovered_idx == i)
                self._panel((rect.x, rect.y, rect.w, rect.h), radius=12,
                            top=_lighten(PANEL_FILL2, 0.12) if hot else PANEL_FILL2,
                            bottom=PANEL_FILL,
                            border=ACCENT if hot else PANEL_LINE,
                            border_w=2, shadow=hot)
                self._text(opt["label"], self.font_medium, ACCENT_SOFT if hot else INK,
                           rect.x + 18, rect.y + 12)
                self._text(opt["desc"], self.font_tiny, INK_DIM, rect.x + 18, rect.y + 38)
                # Pfeil-Dreieck (gezeichnet, kein Glyph -> immer sichtbar)
                ax = rect.x + rect.w - 30
                ay = rect.y + rect.h // 2
                acol = ACCENT if hot else INK_FAINT
                pygame.draw.polygon(self.screen, acol,
                                    [(ax, ay - 8), (ax + 13, ay), (ax, ay + 8)])
                oy += 74
        else:
            # Ergebnis
            res_lines = self._wrap_text(result_text, self.font_medium, pw - 120)
            for i, line in enumerate(res_lines):
                self._text(line, self.font_medium, ACCENT_SOFT, self.w // 2, oy + i * 26, center=True)
            continue_rect = pygame.Rect(self.w // 2 - 100, py + ph - 64, 200, 46)
            self.draw_button("Weiter", continue_rect.x, continue_rect.y,
                             continue_rect.w, continue_rect.h, color=GREEN, pulsing=True)
        return option_rects, continue_rect

    # ═══════════════════════════════════════════════
    # GAME OVER / SIEG
    # ═══════════════════════════════════════════════

    def draw_game_over(self, player, floor_num, score=0, rank=None,
                       lifetime=None, daily_result=None):
        self.draw_background()
        self._dim(150)
        self._text("💀  DU BIST TOT  💀", self.font_huge, RED, self.w // 2, 80, center=True, shadow=True)

        pw = 460
        self._panel((self.w // 2 - pw // 2, 150, pw, 70), radius=14, border=ACCENT)
        self._text(f"PUNKTE: {score:,}".replace(",", "."), self.font_h1, ACCENT,
                   self.w // 2, 162, center=True)
        if daily_result:
            new_best, streak = daily_result
            txt = "📅 Tages-Challenge: NEUE TAGES-BESTLEISTUNG!" if new_best \
                else "📅 Tages-Challenge abgeschlossen"
            if streak > 1:
                txt += f"  ·  🔥 {streak} Tage in Folge!"
            self._text(txt, self.font_small, CYAN, self.w // 2, 196, center=True)
        elif rank == 1:
            self._text("🥇 NEUER REKORD!", self.font_small, ACCENT_SOFT, self.w // 2, 196, center=True)
        elif rank:
            self._text(f"Platz {rank} in der Bestenliste", self.font_small, CYAN, self.w // 2, 196, center=True)

        msgs = [
            f"🏯 Etage {floor_num} erreicht",
            f"🔥 Beste Kombo: x{player.best_combo}" if player.best_combo >= 2 else
            f"🐔 Hühner beschworen: {player.chickens_summoned}",
            f"💰 Gold verdient: {player.gold_earned}",
            f"⚔ Schaden verursacht: {player.damage_dealt}  ·  💥 Größter Treffer: {getattr(player, 'biggest_hit', 0)}",
            f"🎰 Slots gedreht: {player.slots_spun}",
            f"💠 Relikte gesammelt: {len(player.relics)}",
        ]
        for i, msg in enumerate(msgs):
            self._text(msg, self.font_medium, INK, self.w // 2, 250 + i * 34, center=True)

        if lifetime:
            lt = (f"Run #{lifetime.get('runs_played', '?')}  ·  "
                  f"Beste Etage aller Zeiten: {lifetime.get('best_floor', floor_num)}  ·  "
                  f"Kills gesamt: {lifetime.get('total_kills', 0)}")
            self._text(lt, self.font_tiny, INK_DIM, self.w // 2, 250 + 6 * 34, center=True)

        art = assets.fit("ui", "defeat_art", 300, 142)
        if art:
            ax = self.w // 2 - art.get_width() // 2
            self.screen.blit(art, (ax, 474))
            pygame.draw.rect(self.screen, _darken(RED, 0.2),
                             (ax, 474, art.get_width(), art.get_height()), 2, border_radius=6)

        self.draw_button("🏆 Bestenliste", self.w // 2 - 100, self.h - 122, 200, 46,
                         color=PURPLE, text_color=WHITE)
        self._text("R = Neustart   ·   ESC = Beenden", self.font_small, INK_FAINT,
                   self.w // 2, self.h - 56, center=True)

    def draw_victory(self, player, score=0, rank=None):
        self.draw_background()
        t = self._anim_t
        for i in range(16):
            x = int((math.sin(t * 0.5 + i) * 0.5 + 0.5) * self.w)
            y = int((math.cos(t * 0.3 + i * 0.7) * 0.5 + 0.5) * self.h)
            r = int(abs(math.sin(t + i)) * 24 + 8)
            s = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*ACCENT, 40), (r, r), r)
            self.screen.blit(s, (x - r, y - r))

        self._text("🏆 DU HAST GEWONNEN! 🏆", self.font_huge, ACCENT, self.w // 2, 110, center=True, shadow=True)
        self._text("Das Casino hat verloren. Ausnahmsweise.", self.font_title, INK,
                   self.w // 2, 180, center=True)
        self._text(f"PUNKTE: {score:,}".replace(",", "."), self.font_h1, ACCENT,
                   self.w // 2, 226, center=True)
        if rank == 1:
            self._text("🥇 NEUER REKORD!", self.font_small, ACCENT_SOFT, self.w // 2, 264, center=True)
        elif rank:
            self._text(f"Platz {rank} in der Bestenliste", self.font_small, CYAN, self.w // 2, 264, center=True)

        art = assets.fit("ui", "victory_art", 320, 150)
        if art:
            ax = self.w // 2 - art.get_width() // 2
            self.screen.blit(art, (ax, 300))
            pygame.draw.rect(self.screen, _darken(ACCENT, 0.2),
                             (ax, 300, art.get_width(), art.get_height()), 2, border_radius=6)
            stats_y = 300 + art.get_height() + 14
        else:
            stats_y = 310
        msgs = [
            f"🐔 Hühner beschworen: {player.chickens_summoned}",
            f"💰 Gold verdient: {player.gold_earned}",
        ]
        for i, msg in enumerate(msgs):
            self._text(msg, self.font_medium, INK, self.w // 2, stats_y + i * 34, center=True)

        self.draw_button("🏆 Bestenliste", self.w // 2 - 100, self.h - 122, 200, 46,
                         color=PURPLE, text_color=WHITE)
        self._text("R = nochmal   ·   ESC = Beenden", self.font_small, INK_FAINT,
                   self.w // 2, self.h - 56, center=True)

    def draw_update_button(self, version):
        """Update-Hinweis-Button oben rechts im Menü. Gibt das Rect zurück."""
        label = f"🆕 Update {version} laden" if version else "🆕 Update laden"
        w = self.font_small.size(label)[0] + 36
        rect = pygame.Rect(self.w - w - 16, 14, w, 38)
        self.draw_button(label, rect.x, rect.y, rect.w, rect.h,
                         color=GREEN, text_color=BLACK, pulsing=True)
        return rect

    def draw_update_overlay(self, progress):
        """Vollbild-Overlay während des Update-Downloads."""
        self._dim(200)
        pw, ph = 460, 150
        px, py = self.w // 2 - pw // 2, self.h // 2 - ph // 2
        self._panel((px, py, pw, ph), radius=16, border=GREEN, border_w=3)
        if progress.get("error"):
            self._text("Update fehlgeschlagen", self.font_h1, HP_RED,
                       self.w // 2, py + 28, center=True, shadow=True)
            self._text(str(progress["error"])[:48], self.font_small, INK_DIM,
                       self.w // 2, py + 80, center=True)
            return
        self._text("Update wird geladen …", self.font_h1, ACCENT,
                   self.w // 2, py + 26, center=True, shadow=True)
        # Fortschrittsbalken
        bx, by, bw, bh = px + 40, py + 84, pw - 80, 22
        frac = max(0.0, min(1.0, progress.get("frac", 0.0)))
        self._bar(bx, by, bw, bh, frac, GREEN, radius=10)
        self._text(f"{int(frac * 100)} %", self.font_small, WHITE,
                   self.w // 2, by + 2, center=True, shadow=True)
        self._text("Das Spiel startet danach automatisch neu.", self.font_tiny,
                   INK_DIM, self.w // 2, py + ph - 22, center=True)

    def draw_act_clear(self, cleared_act, player, next_act_name=""):
        """'Akt geschafft'-Bildschirm nach einem Boss (Spiel geht endlos weiter)."""
        self.draw_background()
        t = self._anim_t
        for i in range(14):
            x = int((math.sin(t * 0.5 + i) * 0.5 + 0.5) * self.w)
            y = int((math.cos(t * 0.3 + i * 0.7) * 0.5 + 0.5) * self.h)
            r = int(abs(math.sin(t + i)) * 20 + 6)
            s = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*ACCENT, 36), (r, r), r)
            self.screen.blit(s, (x - r, y - r))
        self._dim(60)

        self._text(f"🏆  AKT {cleared_act} GESCHAFFT!", self.font_huge, ACCENT,
                   self.w // 2, 84, center=True, shadow=True)
        self._text("Der Boss ist besiegt. Aber das Casino gibt nicht auf …",
                   self.font_title, INK, self.w // 2, 152, center=True)

        art = assets.fit("ui", "victory_art", 340, 168)
        if art:
            ax = self.w // 2 - art.get_width() // 2
            self.screen.blit(art, (ax, 210))
            pygame.draw.rect(self.screen, _darken(ACCENT, 0.2),
                             (ax, 210, art.get_width(), art.get_height()), 2, border_radius=6)
            ny = 210 + art.get_height() + 18
        else:
            ny = 250

        nxt = f"Auf in Akt {cleared_act + 1}"
        if next_act_name:
            nxt += f": {next_act_name}"
        self._text(nxt + " – es wird härter!", self.font_medium,
                   ACCENT_SOFT, self.w // 2, ny, center=True)
        self._text(f"❤ {player.hp}/{player.max_hp}    💰 {player.gold}    💠 {len(player.relics)} Relikte",
                   self.font_small, INK_DIM, self.w // 2, ny + 34, center=True)

        self.draw_button("Weiter", self.w // 2 - 110, self.h - 110, 220, 50,
                         color=GREEN, text_color=BLACK, pulsing=True)

    # ═══════════════════════════════════════════════
    # HAUPTMENÜ
    # ═══════════════════════════════════════════════

    def draw_main_menu(self, layout):
        t = self._anim_t
        self.draw_background()

        logo = assets.fit("ui", "logo", 720, 240)
        if logo:
            bob = int(4 * math.sin(t * 1.5))
            self.screen.blit(logo, (self.w // 2 - logo.get_width() // 2, 70 + bob))
        else:
            pulse = abs(math.sin(t * 1.5)) * 0.12 + 0.88
            title_color = (int(255 * pulse), int(198 * pulse), int(64 * pulse))
            self._text("🎰  SLOTS & SWORDS  🎰", self.font_huge, title_color,
                       self.w // 2, 120, center=True, shadow=True)


        # Buttons aus dem übergebenen Layout (deckungsgleich mit der Klickerkennung)
        r = layout.get("resume")
        if r:
            self.draw_button("▶ Fortsetzen", r.x, r.y, r.w, r.h, color=GREEN, text_color=BLACK, pulsing=True)
            play_label = "🎮 Neuer Run"
        else:
            play_label = "🎮 SPIELEN"
        p = layout["play"]
        self.draw_button(play_label, p.x, p.y, p.w, p.h, color=ACCENT, text_color=BLACK,
                         pulsing=(r is None))
        d = layout.get("daily")
        if d:
            self.draw_button("📅 Tages-Challenge", d.x, d.y, d.w, d.h,
                             color=CYAN, text_color=BLACK)
            # Heutiger Modifikator + Streak daneben
            mod = daily.modifier_for_today()
            streak = daily.get_streak()
            best = daily.get_today_best()
            info = f"Heute: {mod['name']}"
            if best > 0:
                info += f" · Best: {best:,}".replace(",", ".")
            if streak > 1:
                info += f" · 🔥{streak} Tage"
            if d.collidepoint(self._mouse):
                info = f"{mod['name']}: {mod['desc']}"
            self._text(info, self.font_tiny, INK_DIM, d.right + 12, d.y + d.h // 2 - 7)
        sm = layout.get("slotmode")
        if sm:
            self.draw_button("🎰 Slot-Modus", sm.x, sm.y, sm.w, sm.h,
                             color=GOLD, text_color=BLACK)
            import slotmode as _sm
            best = _sm.load_best()
            if best > 0:
                self._text(f"Best: Runde {best}", self.font_tiny, INK_DIM,
                           sm.right + 12, sm.y + sm.h // 2 - 7)
        tu = layout["tutorial"]
        self.draw_button("📖 Tutorial", tu.x, tu.y, tu.w, tu.h, color=CYAN, text_color=BLACK)
        op = layout["options"]
        self.draw_button("⚙ Optionen", op.x, op.y, op.w, op.h, color=BLUE, text_color=WHITE)
        sc = layout["scores"]
        self.draw_button("🏆 Bestenliste", sc.x, sc.y, sc.w, sc.h, color=PURPLE, text_color=WHITE)
        ac = layout.get("achievements")
        if ac:
            self.draw_button("🎖 Erfolge", ac.x, ac.y, ac.w, ac.h,
                             color=_darken(PURPLE, 0.25), text_color=WHITE)

        cl = layout.get("changelog")
        if cl:
            hot = cl.collidepoint(self._mouse)
            self._chip("🆕 Was ist neu?", self.font_small, cl.x, cl.y,
                       text_col=ACCENT_SOFT if hot else INK_DIM, fill=(*PANEL_FILL, 200),
                       border=ACCENT if hot else PANEL_LINE)

        self._text(f"v{GAME_VERSION}", self.font_tiny, INK_FAINT, self.w - 14, self.h - 22, right=True)

    def draw_changelog(self, entries):
        """Kompakte 'Was ist neu' – eine Version pro Block, lange Zeilen umbrechen."""
        self.draw_background()
        self._dim(150)
        pw, ph = 760, 470
        px, py = self.w // 2 - pw // 2, self.h // 2 - ph // 2 - 10
        self._panel((px, py, pw, ph), radius=18, border=ACCENT, border_w=3)
        self._text("🆕  WAS IST NEU", self.font_huge, ACCENT, self.w // 2,
                   py + 18, center=True, shadow=True)

        text_x = px + 132              # Start der Beschreibung (rechts neben der Pille)
        text_w = px + pw - 24 - text_x  # verfügbare Breite bis zum Panel-Rand
        line_h = 19
        y = py + 84
        for i, (ver, line) in enumerate(entries[:7]):
            newest = (i == 0)
            self._chip(f"v{ver}", self.font_small, px + 24, y + 2,
                       text_col=BLACK if newest else INK,
                       fill=(255, 198, 64, 255) if newest else (*GREY_DARK, 220))
            wrapped = self._wrap_lines(line, self.font_small, text_w, 2)
            for li, seg in enumerate(wrapped):
                self._text(seg, self.font_small, INK if newest else INK_DIM,
                           text_x, y + 2 + li * line_h)
            y += max(40, len(wrapped) * line_h + 16)

        back = pygame.Rect(self.w // 2 - 100, self.h - 62, 200, 44)
        self.draw_button("Zurück", back.x, back.y, back.w, back.h, color=ACCENT, text_color=BLACK)
        return back

    def _wrap_lines(self, text, font, max_w, max_lines):
        """Bricht Text in <= max_lines Zeilen um; letzte Zeile ggf. mit '…'."""
        words = text.split()
        lines, cur = [], ""
        for w in words:
            test = (cur + " " + w).strip()
            if font.size(test)[0] > max_w and cur:
                lines.append(cur)
                cur = w
                if len(lines) == max_lines - 1:
                    break
            else:
                cur = test
        rest = " ".join(words[sum(len(l.split()) for l in lines):]) if lines else text
        # verbleibenden Rest in die letzte Zeile, bei Bedarf kürzen
        if len(lines) < max_lines:
            tail = rest
            while tail and font.size(tail)[0] > max_w:
                tail = tail[:-2]
            if tail != rest and tail:
                tail = tail.rstrip() + "…"
            lines.append(tail if tail else rest)
        return lines

    # ═══════════════════════════════════════════════
    # PFAD-/MAP-SCREEN
    # ═══════════════════════════════════════════════

    NODE_STYLE = {
        "combat":   ("⚔", RED),
        "elite":    ("⭐", ACCENT),
        "event":    ("❓", PURPLE),
        "shop":     ("🏪", GREEN),
        "rest":     ("🔥", ORANGE),
        "treasure": ("💠", CYAN),
        "boss":     ("👑", (255, 90, 90)),
    }

    def draw_map(self, gamemap, current, available, hovered, player, act, message="", act_name=""):
        self.draw_background()
        avail_set = {(n["row"], n["col"]) for n in available}
        cur = tuple(current) if current else None
        hov = tuple(hovered) if hovered else None
        nm = {(n["row"], n["col"]): n for n in gamemap["nodes"]}

        # Kanten zeichnen
        for n in gamemap["nodes"]:
            for r, c in n["next"]:
                t = nm.get((r, c))
                if not t:
                    continue
                glow = cur == (n["row"], n["col"]) and (r, c) in avail_set
                col = ACCENT if glow else (60, 52, 84)
                pygame.draw.line(self.screen, col, (n["x"], n["y"]), (t["x"], t["y"]),
                                 4 if glow else 2)

        # Knoten zeichnen
        for n in gamemap["nodes"]:
            key = (n["row"], n["col"])
            icon, col = self.NODE_STYLE.get(n["type"], ("?", GREY))
            is_av = key in avail_set
            is_done = n["done"]
            is_cur = cur == key
            is_hov = hov == key
            r = mapgen.NODE_R + (3 if (is_hov and is_av) else 0)

            if is_av:
                pulse = 0.5 + 0.5 * math.sin(self._anim_t * 4)
                glow = pygame.Surface((r * 2 + 18, r * 2 + 18), pygame.SRCALPHA)
                pygame.draw.circle(glow, (*ACCENT, int(60 + 70 * pulse)),
                                   (r + 9, r + 9), r + 8)
                self.screen.blit(glow, (n["x"] - r - 9, n["y"] - r - 9))

            fill = _darken(col, 0.55)
            border = ACCENT if is_av else (_lighten(col, 0.2) if not is_done else GREY_DARK)
            if is_done:
                fill = (28, 24, 36)
            pygame.draw.circle(self.screen, fill, (n["x"], n["y"]), r)
            pygame.draw.circle(self.screen, border, (n["x"], n["y"]), r, 3 if is_av else 2)
            if is_cur:
                pygame.draw.circle(self.screen, WHITE, (n["x"], n["y"]), r + 5, 2)

            spr = assets.fit("map", n["type"], int(r * 1.5), int(r * 1.5))
            if spr:
                if is_done:
                    spr = spr.copy(); spr.set_alpha(120)
                self.screen.blit(spr, (n["x"] - spr.get_width() // 2, n["y"] - spr.get_height() // 2))
            else:
                ic = self.font_medium.render(icon, True, WHITE if not is_done else GREY)
                self.screen.blit(ic, (n["x"] - ic.get_width() // 2, n["y"] - ic.get_height() // 2))
            if is_done:
                self._text("✓", self.font_tiny, GREEN, n["x"] + r - 6, n["y"] - r - 2)

        # Kopfzeile / Status
        head = pygame.Surface((self.w, 54), pygame.SRCALPHA)
        head.fill((*DARKER_BG, 230))
        self.screen.blit(head, (0, 0))
        self._text(f"🗺  AKT {act}", self.font_h1, ACCENT, 20, 10, shadow=True)
        if act_name:
            self._text(act_name, self.font_small, INK_DIM, 24, 44, shadow=True)
        # HP / Gold / Relikte rechts
        self._chip(f"❤ {player.hp}/{player.max_hp}", self.font_small, self.w - 430, 14,
                   text_col=WHITE, fill=(60, 20, 20, 170))
        self._chip(f"💰 {player.gold}", self.font_small, self.w - 280, 14,
                   text_col=ACCENT, fill=(60, 45, 12, 170))
        self._chip(f"💠 {len(player.relics)}", self.font_small, self.w - 150, 14,
                   text_col=CYAN, fill=(20, 45, 55, 170))

        # Hinweis / Legende
        if current is None:
            self._text("Wähle deinen Startpunkt ▾", self.font_small, INK_DIM,
                       self.w // 2, self.h - 30, center=True)
        else:
            self._text("Wähle den nächsten Knoten", self.font_small, INK_DIM,
                       self.w // 2, self.h - 30, center=True)

        # Relikt-Tooltip beim Hovern eines Knotens? (Legende stattdessen)
        self._map_legend()

        if message:
            mw = self.font_title.size(message)[0] + 36
            self._panel((self.w // 2 - mw // 2, 60, mw, 38), radius=12,
                        top=(40, 60, 70), bottom=(20, 40, 50), border=CYAN, shadow=True)
            self._text(message, self.font_title, CYAN, self.w // 2, 68, center=True)

    LEGEND = [("combat", "Kampf"), ("elite", "Elite"), ("event", "Event"),
              ("shop", "Shop"), ("rest", "Rast"), ("treasure", "Schatz"), ("boss", "Boss")]

    def _map_legend(self):
        x = 14
        y = self.h - 32
        for ntype, label in self.LEGEND:
            spr = assets.scaled("map", ntype, 22, 22)
            if spr:
                self.screen.blit(spr, (x, y - 5))
                x += 25
            else:
                icon = self.NODE_STYLE.get(ntype, ("?", GREY))[0]
                self._text(icon, self.font_tiny, INK_DIM, x, y)
                x += 18
            x += self._text(label, self.font_tiny, INK_FAINT, x, y) + 16

    def draw_rest(self, player, layout):
        """Lagerfeuer: Heilen oder Karte aufwerten"""
        self.draw_background()
        self._dim(120)
        self._text("🔥  LAGERFEUER", self.font_huge, ORANGE, self.w // 2, 60, center=True, shadow=True)
        self._text("Ein Moment der Ruhe. Nutze ihn weise.", self.font_small, INK_DIM,
                   self.w // 2, 118, center=True)
        mouse = self._mouse

        # ── Aktuelle HP anzeigen (damit man sieht, ob Heilen sich lohnt) ──
        hp, mx = player.hp, player.max_hp
        heal_amt = min(int(mx * 0.3), mx - hp)      # tatsächlich heilbar
        bw, bh = 360, 26
        bx, by = self.w // 2 - bw // 2, 150
        ratio = hp / max(1, mx)
        hp_col = GREEN if ratio > 0.5 else (GOLD if ratio > 0.25 else RED)
        pygame.draw.rect(self.screen, GREY_DARK, (bx, by, bw, bh), border_radius=8)
        if ratio > 0:
            pygame.draw.rect(self.screen, hp_col, (bx, by, int(bw * ratio), bh),
                             border_radius=8)
        # Vorschau des Heilens (heller Abschnitt rechts vom aktuellen HP)
        if heal_amt > 0:
            px2 = bx + int(bw * ratio)
            pw2 = int(bw * (heal_amt / max(1, mx)))
            prev = pygame.Surface((max(1, pw2), bh), pygame.SRCALPHA)
            prev.fill((120, 255, 140, 90))
            self.screen.blit(prev, (px2, by))
        pygame.draw.rect(self.screen, PANEL_LINE, (bx, by, bw, bh), 2, border_radius=8)
        self._text(f"❤ {hp} / {mx} HP", self.font_small, WHITE,
                   self.w // 2, by + 4, center=True)

        for keyname, title, emoji, desc, col in [
            ("heal", "Ausruhen", "❤",
             (f"Heile +{heal_amt} HP\n(30% der Max-HP)" if heal_amt > 0
              else "HP bereits voll –\nkeine Heilung nötig"), GREEN),
            ("upgrade", "Schmieden", "⚒", "Werte eine Karte\ndauerhaft auf (+50%)", ACCENT),
        ]:
            rc = layout[keyname]
            hot = rc.collidepoint(mouse)
            self._panel((rc.x, rc.y - (4 if hot else 0), rc.w, rc.h), radius=16,
                        top=_lighten(PANEL_FILL2, 0.1) if hot else PANEL_FILL2,
                        bottom=PANEL_FILL, border=col if hot else PANEL_LINE, border_w=2)
            oy = rc.y - (4 if hot else 0)
            self._text(emoji, self.font_huge, col, rc.centerx, oy + 10, center=True)
            self._text(title, self.font_title, INK, rc.centerx, oy + 62, center=True)
            for i, line in enumerate(desc.split("\n")):
                self._text(line, self.font_tiny, INK_DIM, rc.centerx, oy + 92 + i * 15, center=True)

        lv = layout["leave"]
        self.draw_button("Weiter (ohne Rast)", lv.x, lv.y, lv.w, lv.h,
                         color=GREY_DARK, text_color=WHITE)

    def draw_pause(self, layout):
        """Pause-/Speichern-Menü über abgedunkeltem Hintergrund"""
        self.draw_background()
        self._dim(170)
        pw, ph = 440, 290
        px, py = self.w // 2 - pw // 2, 232
        self._panel((px, py, pw, ph), radius=18, border=ACCENT, border_w=3)
        self._text("⏸  PAUSE", self.font_h1, ACCENT, self.w // 2, py + 18, center=True, shadow=True)

        r = layout["resume"]
        self.draw_button("▶ Weiter spielen", r.x, r.y, r.w, r.h, color=GREEN, text_color=BLACK, pulsing=True)
        o = layout["options"]
        self.draw_button("⚙ Optionen", o.x, o.y, o.w, o.h, color=BLUE, text_color=WHITE)
        s = layout["save_quit"]
        self.draw_button("💾 Speichern & Beenden", s.x, s.y, s.w, s.h, color=ACCENT, text_color=BLACK)
        m = layout["menu"]
        self.draw_button("🏠 Hauptmenü (ohne Speichern)", m.x, m.y, m.w, m.h, color=GREY_DARK, text_color=WHITE)

    def draw_options(self, layout, opts):
        """Optionsmenü: Lautstärke-Slider + Toggles"""
        self.draw_background()
        self._dim(150)
        panel = layout["panel"]
        self._panel((panel.x, panel.y, panel.w, panel.h), radius=18, border=BLUE, border_w=3)
        self._text("⚙  OPTIONEN", self.font_huge, _lighten(BLUE, 0.3),
                   self.w // 2, panel.y + 16, center=True, shadow=True)

        slabels = {"master": "🔊 Gesamt", "music": "🎵 Musik", "sfx": "💥 Soundeffekte"}
        for key, tr in layout["sliders"].items():
            self._text(slabels[key], self.font_medium, INK, panel.x + 30, tr.y - 9)
            # Track
            pygame.draw.rect(self.screen, GREY_DARK, (tr.x, tr.y, tr.w, tr.h), border_radius=5)
            fw = int(tr.w * opts[key])
            if fw > 0:
                fill = self._panel_surface(fw, tr.h, tr.h // 2, _lighten(BLUE, 0.3),
                                           _darken(BLUE, 0.1), (0, 0, 0), 0)
                self.screen.blit(fill, (tr.x, tr.y))
            # Knob
            kx = tr.x + fw
            pygame.draw.circle(self.screen, WHITE, (kx, tr.y + tr.h // 2), 10)
            pygame.draw.circle(self.screen, _darken(BLUE, 0.2), (kx, tr.y + tr.h // 2), 10, 2)
            self._text(f"{int(opts[key] * 100)}%", self.font_small, ACCENT_SOFT,
                       tr.right + 18, tr.y - 7)

        tlabels = {"fullscreen": "🖥 Vollbild  [F11]", "shake": "📳 Screen-Shake",
                   "particles": "✨ Partikel", "fast": "⏩ Schnell (Animationen)"}
        for key, pill in layout["toggles"].items():
            self._text(tlabels[key], self.font_medium, INK, panel.x + 30, pill.y + 4)
            on = bool(opts[key])
            bg = GREEN_DARK if on else GREY_DARK
            pygame.draw.rect(self.screen, bg, pill, border_radius=pill.h // 2)
            pygame.draw.rect(self.screen, GREEN if on else GREY, pill, 2, border_radius=pill.h // 2)
            knob_x = pill.right - pill.h // 2 if on else pill.x + pill.h // 2
            pygame.draw.circle(self.screen, WHITE, (knob_x, pill.centery), pill.h // 2 - 4)
            self._text("AN" if on else "AUS", self.font_tiny, INK_DIM,
                       pill.x - 8, pill.centery - 7, right=True)

        # Fenstergröße Presets (nur im Fenstermodus aktiv)
        win_btns = layout.get("win_btns", [])
        if win_btns:
            import options as _opt
            dim = bool(opts.get("fullscreen", False))
            self._text("🪟 Fenstergröße (3:2, unverzerrt)", self.font_medium,
                       INK_DIM if dim else INK, panel.x + 30, win_btns[0].y + 6)
            cur_w, cur_h = opts.get("window_w", 1200), opts.get("window_h", 800)
            for i, wr in enumerate(win_btns):
                name, pw, ph = _opt.WINDOW_PRESETS[i]
                active = (pw == cur_w and ph == cur_h) and not dim
                col = ACCENT if active else (GREY_DARK if dim else (50, 50, 70))
                pygame.draw.rect(self.screen, col, wr, border_radius=8)
                pygame.draw.rect(self.screen, _lighten(col, 0.15), wr, 2, border_radius=8)
                tcol = BLACK if active else (INK_FAINT if dim else INK_DIM)
                self._text(name, self.font_tiny, tcol, wr.centerx, wr.centery - 7, center=True)

        b = layout["back"]
        self.draw_button("Zurück", b.x, b.y, b.w, b.h, color=ACCENT, text_color=BLACK)
        d = layout["defaults"]
        self.draw_button("↺ Standard", d.x, d.y, d.w, d.h, color=GREY_DARK, text_color=WHITE)
        self._text("Tipp: [M] Ton stumm · [F11] Vollbild", self.font_tiny, INK_FAINT,
                   self.w // 2, panel.bottom - 28, center=True)

    # ═══════════════════════════════════════════════
    # TUTORIAL
    # ═══════════════════════════════════════════════

    def draw_tutorial(self):
        self.draw_background()
        self._text("📖  WIE MAN SPIELT", self.font_huge, ACCENT, self.w // 2, 20, center=True, shadow=True)

        sections = [
            ("🗺  DER ABLAUF", PURPLE, [
                "Du bewegst dich über eine Pfad-Karte nach oben zum Boss.",
                "Knoten: ⚔ Kampf · ⭐ Elite · ❓ Event · 🏪 Shop · 🔥 Rast · 💠 Schatz.",
                "Nur verbundene Knoten sind wählbar — du entscheidest die Route.",
                "Nach dem Boss beginnt ein härterer Akt. Es geht endlos weiter.",
            ]),
            ("⚔  DEIN ZUG (KARTEN)", CYAN, [
                "Energie (⚡) zahlt Karten — Ungespieltes bleibt in der Hand.",
                "Angriff ⚔ · Verteidigung 🛡 (Block bleibt!) · Special ✨.",
                "COMBO: gleicher Kartentyp hintereinander = Bonus.",
                "Tasten 1-7 = Karte spielen · Leertaste = drehen / weiter.",
            ]),
            ("🎰  SLOTS & GEGNER", ACCENT, [
                "3 gleiche = JACKPOT · Paare & Mix-Synergien geben Extra-Boni.",
                "Synergien: 🐍+🔥 Brandgift · 🎯+💣 Präzision · 💰+👑 Reichtum …",
                "Danach greift der Gegner an: Gold klauen, Gift, Slot blocken …",
                "Slot-Schaden kann den Gegner direkt erledigen.",
            ]),
            ("💠  RELIKTE · RAST · PAUSE", GREEN, [
                "Relikte = permanente Boni (Elite/Boss/Schatz/Event).",
                "Events: Entscheidungen mit Risiko — manche bringen Flüche!",
                "Rast 🔥: heilen ODER Karte schmieden ⚒ (+50%). Shop hat beides.",
                "ESC = Pause: speichern & beenden oder Optionen öffnen.",
            ]),
        ]
        col_w = (self.w - 70) // 2
        for idx, (header, hcolor, lines) in enumerate(sections):
            col, row = idx % 2, idx // 2
            sx = 32 + col * (col_w + 22)
            sy = 100 + row * 200
            self._panel((sx, sy, col_w, 184), radius=14, border=_darken(hcolor, 0.2))
            self._text(header, self.font_title, hcolor, sx + 16, sy + 12)
            pygame.draw.line(self.screen, _darken(hcolor, 0.2), (sx + 16, sy + 40), (sx + col_w - 16, sy + 40))
            for li, line in enumerate(lines):
                self._text("•  " + line, self.font_tiny, INK, sx + 16, sy + 50 + li * 31)

        # Knoten-Legende mit echten Sprites (zeigt, welches Symbol was ist)
        self._text("Knoten auf der Karte:", self.font_small, INK_DIM, self.w // 2, 512, center=True)
        cellw = 150
        total = len(self.LEGEND) * cellw
        lx = self.w // 2 - total // 2
        ly = 542
        for ntype, label in self.LEGEND:
            cx = lx + cellw // 2
            spr = assets.scaled("map", ntype, 40, 40)
            if spr:
                self.screen.blit(spr, (cx - 20, ly))
            else:
                self._text(self.NODE_STYLE.get(ntype, ("?", GREY))[0], self.font_title,
                           WHITE, cx, ly + 6, center=True)
            self._text(label, self.font_tiny, INK, cx, ly + 44, center=True)
            lx += cellw

        back_rect = pygame.Rect(self.w // 2 - 100, self.h - 62, 200, 44)
        self.draw_button("Zurück zum Menü", back_rect.x, back_rect.y, back_rect.w, back_rect.h,
                         color=ACCENT, text_color=BLACK)
        return back_rect

    # ═══════════════════════════════════════════════
    # SHOP
    # ═══════════════════════════════════════════════

    def draw_shop(self, items, player, message="", purchased=None, gamble_bet=25, reroll_cost=0):
        purchased = purchased or set()
        self.draw_background()
        merch = assets.by_height("ui", "merchant", 116)
        if merch:
            self.screen.blit(merch, (18, 10))
        self._text("🏪  DUBIOSER LADEN  🏪", self.font_huge, ACCENT, self.w // 2, 18, center=True, shadow=True)
        self._text("Der Händler riecht nach Bier und schlechten Entscheidungen.",
                   self.font_small, INK_DIM, self.w // 2, 74, center=True)
        self._chip(f"💰 Dein Gold: {player.gold}", self.font_title, self.w // 2 - 90, 100,
                   text_col=ACCENT, fill=(60, 45, 12, 200))
        # Reroll-Button (Items neu mischen) – rechts neben dem Gold
        reroll_rect = pygame.Rect(self.w // 2 + 150, 100, 170, 34)
        can_reroll = reroll_cost > 0 and player.gold >= reroll_cost
        self.draw_button(f"🔄 Neu mischen ({reroll_cost}💰)", reroll_rect.x, reroll_rect.y,
                         reroll_rect.w, reroll_rect.h,
                         color=BLUE if can_reroll else GREY_DARK, text_color=WHITE,
                         disabled=not can_reroll)

        item_rects = []
        item_w, item_h = 196, 156
        spacing = 16
        cols = len(items)
        total_w = cols * item_w + (cols - 1) * spacing
        start_x = self.w // 2 - total_w // 2
        item_y = 150
        mouse = self._mouse

        for i, item in enumerate(items):
            ix = start_x + i * (item_w + spacing)
            rect = pygame.Rect(ix, item_y, item_w, item_h)
            item_rects.append((rect, item))
            sold = item["id"] in purchased
            affordable = (not sold) and player.gold >= item["cost"]
            hovered = rect.collidepoint(mouse) and not sold
            border = ACCENT if (hovered and affordable) else (PANEL_LINE if affordable else GREY_DARK)
            top = _lighten(PANEL_FILL2, 0.1) if (hovered and affordable) else PANEL_FILL2
            self._panel((ix, item_y - (4 if hovered else 0), item_w, item_h), radius=14,
                        top=top, bottom=PANEL_FILL, border=border, border_w=2)
            oy = item_y - (4 if hovered else 0)
            self._text(item["emoji"], self.font_large, WHITE, ix + item_w // 2, oy + 10, center=True)
            self._text(item["name"], self.font_small, INK if affordable else GREY,
                       ix + item_w // 2, oy + 54, center=True)
            desc_lines = self._wrap_text(item["desc"], self._font_micro, item_w - 18)
            for li, line in enumerate(desc_lines[:3]):
                self._text(line, self._font_micro, INK_DIM, ix + 10, oy + 78 + li * 13)
            if sold:
                self._text("✓ GEKAUFT", self.font_medium, GREEN,
                           ix + item_w // 2, oy + item_h - 26, center=True)
                veil = pygame.Surface((item_w, item_h), pygame.SRCALPHA)
                veil.fill((0, 0, 0, 130))
                self.screen.blit(veil, (ix, oy))
            else:
                price_col = ACCENT if affordable else RED
                self._text(f"💰 {item['cost']}", self.font_medium, price_col,
                           ix + item_w // 2, oy + item_h - 26, center=True)

        # Glücksrad
        gamble_rect = pygame.Rect(self.w // 2 - 330, 330, 310, 170)
        gh = gamble_rect.collidepoint(mouse)
        self._panel((gamble_rect.x, gamble_rect.y, gamble_rect.w, gamble_rect.h), radius=14,
                    border=PURPLE if gh else PURPLE_DARK, border_w=2)
        self._text("🎰  GLÜCKSRAD", self.font_title, _lighten(PURPLE, 0.4),
                   gamble_rect.centerx, gamble_rect.y + 14, center=True)
        for li, line in enumerate([f"Einsatz: {gamble_bet} Gold", "Gewinne bis zu 8×!", "(Jeder Dreh wird teurer. Haus gewinnt.)"]):
            self._text(line, self._font_micro, INK_DIM, gamble_rect.centerx, gamble_rect.y + 54 + li * 16, center=True)
        can_gamble = player.gold >= gamble_bet
        self.draw_button(f"🎲 DREHEN ({gamble_bet}💰)", gamble_rect.x + 55, gamble_rect.y + 116, 200, 40,
                         color=PURPLE if can_gamble else GREY_DARK, text_color=WHITE, disabled=not can_gamble)

        # Zustands-Panel
        info_rect = pygame.Rect(self.w // 2 + 20, 330, 310, 170)
        self._panel((info_rect.x, info_rect.y, info_rect.w, info_rect.h), radius=14)
        self._text("📊 DEIN ZUSTAND", self.font_small, ACCENT, info_rect.x + 14, info_rect.y + 12)
        stats = [
            f"❤ HP: {player.hp}/{player.max_hp}",
            f"💪 Stärke: {player.strength}    ⚡ Energie: {player.max_energy}",
            f"🍀 Glücksrunden: {player.lucky}",
            f"🃏 Deck: {len(player.deck) + len(player.discard) + len(player.hand)}    💠 Relikte: {len(player.relics)}",
        ]
        for li, line in enumerate(stats):
            self._text(line, self.font_small, INK, info_rect.x + 16, info_rect.y + 42 + li * 26)

        if message:
            mw = self.font_title.size(message)[0] + 36
            mx = self.w // 2 - mw // 2
            self._panel((mx, 516, mw, 40), radius=12, top=(40, 60, 70), bottom=(20, 40, 50),
                        border=CYAN, shadow=True)
            self._text(message, self.font_title, CYAN, self.w // 2, 524, center=True)

        leave_rect = pygame.Rect(self.w // 2 - 150, self.h - 72, 300, 50)
        self.draw_button("Weiter zur nächsten Etage", leave_rect.x, leave_rect.y,
                         leave_rect.w, leave_rect.h, color=GREEN, text_color=BLACK, pulsing=True)
        return item_rects, gamble_rect, leave_rect, reroll_rect

    def draw_card_grid(self, player, title, accent, only_upgradeable=False, scroll=0):
        """Karten-Auswahlraster (Verbrennen oder Aufwerten). Gibt [(rect, card)] zurück.
        scroll = Anzahl ausgeblendeter Reihen oben (Mausrad)."""
        self._dim(215)
        self._text(title, self.font_h1, accent, self.w // 2, 26, center=True, shadow=True)
        if only_upgradeable:
            self._text("Nur aufwertbare Karten sind anklickbar.", self.font_small, INK_DIM,
                       self.w // 2, 66, center=True)

        all_cards = player.deck + player.discard + player.hand
        rects = []
        card_w, card_h = 112, 152
        per_row = 8
        spacing = 12
        start_x = self.w // 2 - (per_row * (card_w + spacing) - spacing) // 2
        start_y = 92
        mouse = self._mouse

        total_rows = (len(all_cards) + per_row - 1) // per_row
        visible_rows = max(1, (self.h - 90 - start_y + spacing) // (card_h + spacing))
        scroll = max(0, min(scroll, max(0, total_rows - visible_rows)))

        for i, card in enumerate(all_cards):
            row, col = i // per_row, i % per_row
            if row < scroll:
                continue
            cx = start_x + col * (card_w + spacing)
            cy = start_y + (row - scroll) * (card_h + spacing)
            if cy + card_h > self.h - 90:
                break
            selectable = (not only_upgradeable) or card.can_upgrade()
            rect = pygame.Rect(cx, cy, card_w, card_h)
            hov = rect.collidepoint(mouse) and selectable
            self._draw_card(card, pygame.Rect(cx, cy - (8 if hov else 0), card_w, card_h), hovered=hov)
            if not selectable:
                veil = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
                veil.fill((0, 0, 0, 150))
                self.screen.blit(veil, (cx, cy))
            if selectable:
                rects.append((rect, card))

        # Scroll-Hinweis + schlanker Balken rechts, wenn nicht alles passt
        if total_rows > visible_rows:
            self._text(f"Mausrad: scrollen ({scroll + 1}–{min(total_rows, scroll + visible_rows)} von {total_rows} Reihen)",
                       self.font_tiny, INK_DIM, self.w // 2, self.h - 88, center=True)
            track_x = start_x + per_row * (card_w + spacing) + 4
            track_y, track_h = start_y, visible_rows * (card_h + spacing) - spacing
            pygame.draw.rect(self.screen, GREY_DARK, (track_x, track_y, 6, track_h), border_radius=3)
            thumb_h = max(24, int(track_h * visible_rows / total_rows))
            denom = max(1, total_rows - visible_rows)
            thumb_y = track_y + int((track_h - thumb_h) * scroll / denom)
            pygame.draw.rect(self.screen, accent, (track_x, thumb_y, 6, thumb_h), border_radius=3)

        self.draw_button("Abbrechen", self.w // 2 - 80, self.h - 70, 160, 42,
                         color=GREY_DARK, text_color=WHITE)
        return rects

    # ═══════════════════════════════════════════════
    # KLASSENAUSWAHL
    # ═══════════════════════════════════════════════

    def draw_class_select(self, classes, daily=False):
        """Klassenauswahl vor dem Run. Gibt ([rects], back_rect) zurück."""
        self.draw_background()
        title = "📅 Tages-Challenge – wähle deine Klasse" if daily else "Wähle deine Klasse"
        self._text(title, self.font_huge, ACCENT, self.w // 2, 40, center=True, shadow=True)
        self._text("Jede Klasse bringt ein eigenes Startdeck und ein Start-Relikt mit.",
                   self.font_small, INK_DIM, self.w // 2, 100, center=True)

        mouse = self._mouse
        n = len(classes)
        gap = 20
        ch = 290                       # kompakte Karten – Details kommen beim Hovern
        cw = min(240, (self.w - 60 - (n - 1) * gap) // max(1, n))
        total = n * cw + (n - 1) * gap
        sx0 = self.w // 2 - total // 2
        sy = 150
        rects = []
        hovered = None
        for i, c in enumerate(classes):
            x = sx0 + i * (cw + gap)
            rect = pygame.Rect(x, sy, cw, ch)
            hov = rect.collidepoint(mouse)
            accent = c.get("color", ACCENT)
            if hov:
                hovered = (c, x, accent)
            self._panel((x, sy - (6 if hov else 0), cw, ch), radius=16,
                        border=accent if hov else _darken(accent, 0.3),
                        border_w=3 if hov else 2)
            oy = sy - (6 if hov else 0)
            # Portrait-Sprite (Fallback: Emoji)
            portrait = assets.by_height("ui", f"class_{c['id']}", 110)
            if portrait:
                self.screen.blit(portrait, (x + cw // 2 - portrait.get_width() // 2, oy + 14))
            else:
                self._text(c["emoji"], self.font_huge, accent, x + cw // 2, oy + 40, center=True)
            self._text(c["name"], self.font_h1, _lighten(accent, 0.2),
                       x + cw // 2, oy + 132, center=True, shadow=True)
            # Kurz-Beschreibung (1–2 Zeilen)
            for li, line in enumerate(self._wrap_text(c["desc"], self.font_tiny, cw - 28)[:2]):
                self._text(line, self.font_tiny, INK_DIM, x + cw // 2, oy + 174 + li * 16, center=True)
            # Button
            btn = pygame.Rect(x + 26, oy + ch - 50, cw - 52, 38)
            self.draw_button("Wählen", btn.x, btn.y, btn.w, btn.h,
                             color=accent, text_color=BLACK, pulsing=hov)
            rects.append(rect)

        # ── Detail-Panel beim Hovern (volle Infos) ──
        py = sy + ch + 22
        pw, ph = 760, 196
        px = self.w // 2 - pw // 2
        if hovered:
            c, _cx, accent = hovered
            self._panel((px, py, pw, ph), radius=16, border=accent, border_w=2)
            self._text(f"{c['emoji']}  {c['name']}", self.font_title, _lighten(accent, 0.2),
                       px + 24, py + 14, shadow=True)
            for li, line in enumerate(self._wrap_text(c["desc"], self.font_small, pw - 48)):
                self._text(line, self.font_small, INK, px + 24, py + 48 + li * 20)
            for li, line in enumerate(self._wrap_text("⭐ " + c["perk"], self.font_small, pw - 48)):
                self._text(line, self.font_small, ACCENT_SOFT, px + 24, py + 90 + li * 20)
            # Startdeck (in Spalten)
            from collections import Counter
            self._text("🃏 Startdeck:", self.font_small, INK_DIM, px + 24, py + ph - 56)
            items = [f"{cnt}× {name}" if cnt > 1 else name
                     for name, cnt in Counter(c["deck"]).items()]
            per_col = (len(items) + 2) // 3
            for idx, label in enumerate(items):
                col, row = idx // per_col, idx % per_col
                self._text("•  " + label, self.font_tiny, INK,
                           px + 150 + col * 210, py + ph - 56 + row * 16)
        else:
            self._text("Fahre über eine Klasse für alle Details.", self.font_small,
                       INK_FAINT, self.w // 2, py + ph // 2 - 10, center=True)

        back = pygame.Rect(self.w // 2 - 100, self.h - 56, 200, 40)
        self.draw_button("Zurück", back.x, back.y, back.w, back.h,
                         color=GREY_DARK, text_color=WHITE)
        return rects, back

    # ═══════════════════════════════════════════════
    # ERFOLGE
    # ═══════════════════════════════════════════════

    def draw_achievement_toasts(self, toasts):
        """Erfolgs-Einblendungen oben rechts (gestapelt, mit Einfade-Slide)."""
        y = 84
        for adef, t in toasts[:3]:
            # Slide-in in den ersten 0.3s, Fade-out in den letzten 0.6s
            age = 4.5 - t
            slide = max(0.0, 1.0 - age / 0.3) if age < 0.3 else 0.0
            alpha = min(1.0, t / 0.6)
            w, h = 320, 64
            x = self.w - w - 16 + int(slide * (w + 24))
            box = pygame.Surface((w, h), pygame.SRCALPHA)
            pygame.draw.rect(box, (18, 14, 30, int(235 * alpha)), (0, 0, w, h), border_radius=12)
            pygame.draw.rect(box, (*ACCENT, int(255 * alpha)), (0, 0, w, h), 2, border_radius=12)
            self.screen.blit(box, (x, y))
            self._text(f"{adef['emoji']} Erfolg: {adef['name']}", self.font_medium, ACCENT,
                       x + 14, y + 9, shadow=True)
            self._text(adef["desc"], self.font_tiny, INK, x + 14, y + 36)
            y += h + 10

    def draw_achievements(self, defs, is_unlocked, prog):
        """Erfolge-Übersicht (2 Spalten). Gibt das Zurück-Rect zurück."""
        self.draw_background()
        done, total = prog
        self._text("🎖  ERFOLGE", self.font_huge, ACCENT, self.w // 2, 30, center=True, shadow=True)
        self._text(f"{done} von {total} freigeschaltet", self.font_small, INK_DIM,
                   self.w // 2, 86, center=True)

        cols = 2
        cell_w, cell_h, gap = 560, 46, 8
        start_x = self.w // 2 - (cols * cell_w + (cols - 1) * gap) // 2
        start_y = 104
        for i, d in enumerate(defs):
            row, col = i // cols, i % cols
            x = start_x + col * (cell_w + gap)
            y = start_y + row * (cell_h + gap)
            unlocked = is_unlocked(d["id"])
            self._panel((x, y, cell_w, cell_h), radius=10,
                        border=ACCENT if unlocked else PANEL_LINE,
                        border_w=2, shadow=False)
            # Schaltet dieser Erfolg Inhalte frei?
            rewards = achievements.rewards_for(d["id"])
            if unlocked:
                self._text(d["emoji"], self.font_medium, WHITE, x + 12, y + 8)
                self._text(d["name"], self.font_small, ACCENT, x + 46, y + 4)
                self._text(d["desc"], self.font_tiny, INK, x + 46, y + 25)
            else:
                self._text("🔒", self.font_medium, GREY, x + 12, y + 8)
                self._text("???", self.font_small, GREY, x + 46, y + 4)
                self._text(d["desc"], self.font_tiny, INK_FAINT, x + 46, y + 25)
            if rewards:
                names = ", ".join(n for _k, n in rewards)
                tag = ("🔓 " + names) if unlocked else "🎁 schaltet Inhalt frei"
                self._text(tag, self.font_tiny, GREEN if unlocked else ACCENT_SOFT,
                           x + cell_w - 14, y + 14, right=True)

        back = pygame.Rect(self.w // 2 - 100, self.h - 58, 200, 44)
        self.draw_button("Zurück", back.x, back.y, back.w, back.h,
                         color=ACCENT, text_color=BLACK)
        return back

    # ═══════════════════════════════════════════════
    # SLOT-MODUS (eigenständiges Spiel)
    # ═══════════════════════════════════════════════

    def draw_slotmode(self, run, machine, spinning, spin_btn, cashout_btn,
                      lucky_btn, shop_lay, back_rect):
        self.draw_background()
        self._dim(120)
        if run is None:
            return
        self._text("🎰  DAS LOCH", self.font_huge, GOLD, self.w // 2, 12,
                   center=True, shadow=True)
        self.draw_button("← Menü", back_rect.x, back_rect.y, back_rect.w, back_rect.h,
                         color=GREY_DARK, text_color=WHITE)

        # Kopf-Statusleiste
        met = run.coins >= run.quota
        chips = [
            (f"Runde {run.round}", PURPLE),
            (f"🏠 Miete: {run.quota}", GREEN if met else ACCENT),
            (f"🪙 {run.coins}", GOLD),
            (f"🎲 Drehs: {run.spins_left}", CYAN if run.spins_left > 1 else RED),
            (f"🍀 Glück: {run.lucky}", _lighten(GREEN, 0.3)),
        ]
        cx = 180
        for label, col in chips:
            self._chip(label, self.font_medium, cx, 60, text_col=col,
                       fill=(20, 18, 34, 210))
            cx += self.font_medium.size(label)[0] + 40

        # Fortschrittsbalken zur Miete
        bar = pygame.Rect(self.w // 2 - 320, 100, 640, 16)
        pygame.draw.rect(self.screen, GREY_DARK, bar, border_radius=8)
        frac = min(1.0, run.coins / max(1, run.quota))
        if frac > 0:
            col = GREEN if met else GOLD
            pygame.draw.rect(self.screen, col, (bar.x, bar.y, int(bar.w * frac), bar.h),
                             border_radius=8)
        pygame.draw.rect(self.screen, PANEL_LINE, bar, 2, border_radius=8)
        self._text(f"{run.coins} / {run.quota}", self.font_tiny,
                   BLACK if frac > 0.5 else INK, bar.centerx, bar.y + 1, center=True)

        # Boss-Runden-Banner
        if getattr(run, "boss_mod", None):
            bw = 660
            br = pygame.Rect(self.w // 2 - bw // 2, 124, bw, 24)
            pygame.draw.rect(self.screen, (60, 16, 22), br, border_radius=10)
            pygame.draw.rect(self.screen, RED, br, 2, border_radius=10)
            self._text(f"⚠️ BOSS-RUNDE: {run.boss_mod['label']}", self.font_tiny,
                       _lighten(RED, 0.4), br.centerx, br.y + 5, center=True)
        elif run.log:
            self._text(run.log[0], self.font_small, INK_DIM, self.w // 2, 132, center=True)

        # Der echte 3-Walzen-Automat (Symbol-Sprites)
        if machine:
            machine.draw(self.screen, self.font_title, self.font_large,
                         self.font_small, self.font_tiny)

        # Charms links, Beutel rechts, Wertung darunter
        self._slotmode_charms(run, 14, 156)
        self._slotmode_bag(run, self.w - 210, 156)
        self._slotmode_breakdown(run, spin_btn.bottom + 14)

        # Spin-Phase: Buttons
        if not run.in_shop and not run.game_over:
            label = "🎰  DREHEN" if not spinning else "…dreht…"
            self.draw_button(label, spin_btn.x, spin_btn.y, spin_btn.w, spin_btn.h,
                             color=GOLD if not spinning else GREY_DARK,
                             text_color=BLACK, pulsing=not spinning)
            self._text("Leertaste = drehen", self.font_tiny, INK_FAINT,
                       spin_btn.centerx, spin_btn.bottom + 4, center=True)
            if met and run.spins_left > 0 and not spinning:
                self.draw_button("💵 Miete zahlen", cashout_btn.x, cashout_btn.y,
                                 cashout_btn.w, cashout_btn.h, color=GREEN,
                                 text_color=BLACK, pulsing=True)
            # Glücksdreh: Glück ausgeben für einen pechfreien Dreh
            if not spinning and lucky_btn:
                can = run.can_lucky_spin()
                cost = getattr(run, "LUCKY_SPIN_COST", 4)
                lbl = f"🍀 Glücksdreh ({cost})" if can else f"🍀 Glück {run.lucky}/{cost}"
                if getattr(run, "next_lucky_spin", False):
                    lbl = "🍀 bereit!"
                self.draw_button(lbl, lucky_btn.x, lucky_btn.y, lucky_btn.w, lucky_btn.h,
                                 color=GREEN if can else GREY_DARK,
                                 text_color=BLACK if can else INK_DIM)

        if run.in_shop:
            self._slotmode_shop(run, shop_lay)
        elif run.game_over:
            self._slotmode_gameover(run)

    def _slotmode_charms(self, run, x, y):
        self._panel((x, y, 188, 430), radius=12, border=PURPLE, border_w=2)
        self._text(f"🃏 Charms {len(run.charms)}/6", self.font_medium,
                   _lighten(PURPLE, 0.3), x + 12, y + 8)
        if not run.charms:
            self._text("— noch keine —", self.font_tiny, INK_FAINT, x + 12, y + 40)
        for i, cid in enumerate(run.charms):
            c = slotmode.CHARM_BY_ID.get(cid, {})
            jy = y + 40 + i * 64
            spr = assets.fit("jokers", cid, 28, 28)
            if spr:
                self.screen.blit(spr, (x + 10, jy)); tx = x + 44
            else:
                self._text(c.get("emoji", "?"), self.font_medium, WHITE, x + 12, jy)
                tx = x + 42
            self._text(c.get("name", ""), self.font_small, ACCENT, tx, jy)
            self._draw_wrapped(c.get("desc", ""), self.font_tiny, INK_DIM,
                               x + 12, jy + 22, 172, 13, 3)

    def _slotmode_bag(self, run, x, y):
        self._panel((x, y, 196, 430), radius=12, border=BLUE, border_w=2)
        self._text("🎒 Beutel", self.font_medium, _lighten(BLUE, 0.3), x + 12, y + 8)
        total = sum(run.bag.values())
        self._text(f"{total} Symbole", self.font_tiny, INK_DIM, x + 12, y + 34)
        items = sorted(run.bag.items(),
                       key=lambda kv: -run.values.get(kv[0], 0) if kv[0] not in
                       ("TRAP", "PIT", "CURSE") else 99)
        for i, (name, cnt) in enumerate(items[:16]):
            iy = y + 54 + i * 22
            neg = name in ("TRAP", "PIT", "CURSE")
            val = run.values.get(name, 0)
            self._text(f"{slotmode.EMOJI.get(name,'?')} ×{cnt}", self.font_tiny,
                       RED if neg else INK, x + 12, iy)
            self._text("Pech" if neg else f"{val}", self.font_tiny,
                       RED if neg else GOLD, x + 184, iy, right=True)

    def _slotmode_breakdown(self, run, y):
        if not run.last_lines:
            return
        lines = run.last_lines[-9:]
        bx = self.w // 2 - 210
        bh = 26 + len(lines) * 18
        self._panel((bx, y, 420, bh), radius=10, border=PANEL_LINE)
        self._text("Letzter Dreh", self.font_small, INK_DIM, bx + 12, y + 5)
        for i, (left, right) in enumerate(lines):
            ly = y + 26 + i * 18
            last = (i == len(lines) - 1)
            self._text(left, self.font_tiny, ACCENT if last else INK, bx + 12, ly)
            self._text(right, self.font_tiny, GOLD if last else INK_DIM,
                       bx + 408, ly, right=True)

    def _slotmode_shop(self, run, lay):
        self._dim(165)
        self._text("🛒  MIETE BEZAHLT — bau deinen Automaten aus",
                   self.font_title, GOLD, self.w // 2, 240, center=True, shadow=True)
        self._chip(f"🪙 {run.coins}", self.font_title, self.w // 2 - 36, 286,
                   text_col=GOLD, fill=(50, 40, 10, 220))
        kind_lbl = {"symbol": "Symbol", "upgrade": "Upgrade", "charm": "Charm",
                    "remove": "Entfernen", "payline": "Linie"}
        for i, rect in enumerate(lay["offers"]):
            if i >= len(run.shop):
                continue
            o = run.shop[i]
            bought = o.get("bought")
            afford = run.can_afford(o) and not bought
            border = GREEN if bought else (ACCENT if afford else GREY_DARK)
            self._panel((rect.x, rect.y, rect.w, rect.h), radius=12, border=border, border_w=2)
            self._text(kind_lbl.get(o["kind"], ""), self.font_small,
                       _lighten(border, 0.2), rect.x + 12, rect.y + 10)
            if o["kind"] == "charm":
                spr = assets.fit("jokers", o["charm"], 46, 46)
                if spr:
                    self.screen.blit(spr, (rect.right - 56, rect.y + 8))
            self._draw_wrapped(o["label"], self.font_medium, INK,
                               rect.x + 12, rect.y + 36, rect.w - 24, 21, 3)
            if o["kind"] == "charm":
                self._draw_wrapped(slotmode.CHARM_BY_ID[o["charm"]]["desc"], self.font_tiny,
                                   INK_DIM, rect.x + 12, rect.y + 96, rect.w - 24, 14, 4)
            if bought:
                self._text("✓ gekauft", self.font_small, GREEN, rect.centerx,
                           rect.bottom - 30, center=True)
            else:
                self._text(f"🪙 {o['cost']}", self.font_medium,
                           GOLD if afford else RED, rect.centerx, rect.bottom - 32, center=True)
        # Telefon-Deal
        if lay.get("phone") and run.phone:
            pr = lay["phone"]
            pygame.draw.rect(self.screen, (40, 16, 50), pr, border_radius=10)
            pygame.draw.rect(self.screen, PURPLE, pr, 2, border_radius=10)
            self._text("📞 " + run.phone["label"], self.font_small,
                       _lighten(PURPLE, 0.4), pr.centerx, pr.y + 12, center=True)
        rr = lay["reroll"]
        self.draw_button(f"🔄 Neu ({run.reroll_cost})", rr.x, rr.y, rr.w, rr.h,
                         color=BLUE if run.coins >= run.reroll_cost else GREY_DARK,
                         text_color=WHITE)
        co = lay["continue"]
        self.draw_button("Nächste Runde ▶", co.x, co.y, co.w, co.h, color=GREEN,
                         text_color=BLACK, pulsing=True)

    def _slotmode_gameover(self, run):
        self._dim(190)
        pw, ph = 500, 250
        px, py = self.w // 2 - pw // 2, self.h // 2 - ph // 2
        self._panel((px, py, pw, ph), radius=16, border=RED, border_w=3)
        self._text("✋  DIE HAND HOLT DICH", self.font_h1, RED, self.w // 2, py + 22,
                   center=True, shadow=True)
        self._text(f"Du hast Runde {run.round} erreicht.", self.font_title, INK,
                   self.w // 2, py + 84, center=True)
        self._text(f"Miete verfehlt: {run.coins} / {run.quota}", self.font_medium,
                   INK_DIM, self.w // 2, py + 122, center=True)
        self._text(f"🏆 Beste Runde: {run.best_round}", self.font_medium, GOLD,
                   self.w // 2, py + 150, center=True)
        bx = pygame.Rect(self.w // 2 - 110, py + ph - 54, 220, 44)
        self.draw_button("Zurück zum Menü", bx.x, bx.y, bx.w, bx.h,
                         color=ACCENT, text_color=BLACK, pulsing=True)

    def _draw_wrapped(self, text, font, color, x, y, max_w, line_h, max_lines):
        """Zeichnet umgebrochenen Text (für Slot-Modus-Tooltips/Shop-Karten)."""
        words = text.split()
        line, count = "", 0
        for w in words:
            test = (line + " " + w).strip()
            if font.size(test)[0] > max_w and line:
                self._text(line, font, color, x, y + count * line_h)
                count += 1; line = w
                if count >= max_lines - 1:
                    break
            else:
                line = test
        if line and count < max_lines:
            self._text(line, font, color, x, y + count * line_h)

    # ═══════════════════════════════════════════════
    # HIGHSCORES
    # ═══════════════════════════════════════════════

    def draw_scores(self, scores):
        self.draw_background()
        self._text("🏆  BESTENLISTE  🏆", self.font_huge, ACCENT, self.w // 2, 36, center=True, shadow=True)

        pw, ph = 800, 540
        px, py = self.w // 2 - pw // 2, 110
        self._panel((px, py, pw, ph), radius=16)

        if not scores:
            self._text("Noch keine Einträge. Geh sterben (im Spiel).", self.font_title,
                       INK_DIM, self.w // 2, py + 200, center=True)
        else:
            cols = [("#", px + 40), ("Punkte", px + 110), ("Etage", px + 300),
                    ("Gold", px + 420), ("🐔", px + 540), ("Datum", px + 620)]
            header_y = py + 24
            for label, cx in cols:
                self._text(label, self.font_small, ACCENT, cx, header_y)
            pygame.draw.line(self.screen, _darken(ACCENT, 0.2),
                             (px + 30, header_y + 26), (px + pw - 30, header_y + 26), 2)

            for i, entry in enumerate(scores[:10]):
                ry = header_y + 40 + i * 44
                if i % 2 == 0:
                    row = pygame.Surface((pw - 40, 38), pygame.SRCALPHA)
                    row.fill((255, 255, 255, 8))
                    self.screen.blit(row, (px + 20, ry - 6))
                rank_str = {0: "🥇", 1: "🥈", 2: "🥉"}.get(i, f"{i+1}")
                row_color = ACCENT if i == 0 else (INK if i < 3 else INK_DIM)
                won = " 👑" if entry.get("won") else ""
                vals = [
                    (rank_str, px + 40),
                    (f"{entry.get('score', 0):,}".replace(",", "."), px + 110),
                    (str(entry.get('floor', '?')) + won, px + 300),
                    (str(entry.get('gold', 0)), px + 420),
                    (str(entry.get('chickens', 0)), px + 540),
                    (entry.get('date', ''), px + 620),
                ]
                for val, cx in vals:
                    self._text(val, self.font_small, row_color, cx, ry)

        back_rect = pygame.Rect(self.w // 2 - 90, self.h - 66, 180, 44)
        self.draw_button("Zurück", back_rect.x, back_rect.y, back_rect.w, back_rect.h,
                         color=ACCENT, text_color=BLACK)
        return back_rect
