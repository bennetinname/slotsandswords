"""UI-Renderer: Alle Zeichenfunktionen für das Spiel (modernes Design)"""

import pygame
import math
from constants import *
import mapgen
import assets


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
        self.font_large  = pygame.font.SysFont("Segoe UI Emoji", 34)
        self.font_medium = pygame.font.SysFont("Segoe UI Emoji", 19, bold=True)
        self.font_small  = pygame.font.SysFont("Segoe UI Emoji", 15)
        self.font_tiny   = pygame.font.SysFont("Segoe UI Emoji", 13)
        self._font_micro = pygame.font.SysFont("Segoe UI Emoji", 11)
        self._font_nano  = pygame.font.SysFont("Segoe UI Emoji", 9)

        self._anim_t = 0.0

        # Caches für teure Surfaces
        self._panel_cache = {}
        self._shadow_cache = {}
        self._grad_cache = {}

        self._build_background()

    def tick(self, dt):
        self._anim_t += dt

    # ═══════════════════════════════════════════════
    # LOW-LEVEL HELFER (modernes Aussehen)
    # ═══════════════════════════════════════════════

    def _build_background(self):
        """Erzeugt einmalig den Hintergrund (gemaltes Bild ODER Gradient) mit Vignette"""
        bg = pygame.Surface((self.w, self.h)).convert()
        scene = assets.load("ui", "bg_kneipe")
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

        self._bg = bg

    def draw_background(self):
        """Zeichnet den vorberechneten Hintergrund + dezente Animation"""
        self.screen.blit(self._bg, (0, 0))
        # Schwebende, sehr dezente Symbole
        t = self._anim_t
        glyphs = ["♠", "♥", "♦", "♣", "🎰", "💰", "🍀", "⭐"]
        for i, g in enumerate(glyphs):
            ph = i * 1.7
            x = (math.sin(t * 0.12 + ph) * 0.5 + 0.5) * self.w
            y = ((t * 14 + i * 110) % (self.h + 100)) - 50
            surf = self.font_large.render(g, True, _lighten(BG_TOP, 0.12))
            surf.set_alpha(26)
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
            fill = self._panel_surface(fw, h, min(radius, h // 2),
                                       _lighten(col, 0.3), _darken(col, 0.15),
                                       (0, 0, 0), 0)
            self.screen.blit(fill, (x, y))
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

    def draw_status_bar(self, player, enemy, floor_num, turn_num):
        """Oben: Spieler-Status, Etage, Runde — als moderne Leiste"""
        bar_h = 70
        # Hintergrundleiste
        strip = pygame.Surface((self.w, bar_h), pygame.SRCALPHA)
        pygame.draw.rect(strip, (*DARKER_BG, 235), (0, 0, self.w, bar_h))
        self.screen.blit(strip, (0, 4))
        pygame.draw.line(self.screen, _darken(ACCENT, 0.4), (0, 4 + bar_h), (self.w, 4 + bar_h), 2)

        # HP-Bar
        hp_ratio = player.hp / player.max_hp
        hp_color = HP_GREEN if hp_ratio > 0.5 else (ORANGE if hp_ratio > 0.25 else HP_RED)
        bx, by, bw, bh = 14, 14, 210, 20
        self._bar(bx, by, bw, bh, hp_ratio, hp_color, radius=10)
        self._text(f"❤ {player.hp}/{player.max_hp}", self.font_small, WHITE,
                   bx + 10, by + 2, shadow=True)

        # Block (unter HP)
        col_x = bx
        cy = by + bh + 4
        if player.block > 0:
            w, _ = self._chip(f"🛡 {player.block}", self.font_tiny, col_x, cy,
                              text_col=CYAN, fill=(*BLUE_DARK, 150))
            col_x += w + 6
        if player.strength > 0:
            w, _ = self._chip(f"💪 {player.strength}", self.font_tiny, col_x, cy,
                              text_col=ORANGE, fill=(60, 35, 10, 160))
            col_x += w + 6
        if player.burn > 0:
            self._chip(f"🔥 {player.burn}", self.font_tiny, col_x, cy,
                       text_col=ORANGE, fill=(60, 25, 10, 160))

        # Energie & Gold (Mitte-links)
        self._chip(f"⚡ {player.energy}/{player.max_energy}", self.font_medium, 240, 12,
                   text_col=CYAN, fill=(20, 50, 70, 170))
        self._chip(f"💰 {player.gold}", self.font_medium, 240, 42,
                   text_col=ACCENT, fill=(60, 45, 10, 170))

        # Etage / Runde (Mitte) als Pille
        center_txt = f"ETAGE {floor_num}  ·  RUNDE {turn_num}"
        tw = self.font_title.size(center_txt)[0]
        px = self.w // 2 - tw // 2 - 16
        pill = pygame.Surface((tw + 32, 34), pygame.SRCALPHA)
        pygame.draw.rect(pill, (*PANEL_FILL, 230), (0, 0, tw + 32, 34), border_radius=17)
        pygame.draw.rect(pill, _darken(ACCENT, 0.3), (0, 0, tw + 32, 34), 1, border_radius=17)
        self.screen.blit(pill, (px, 14))
        self._text(center_txt, self.font_title, ACCENT, self.w // 2, 18, center=True)

        # Gegner-Status rechts
        if enemy and enemy.is_alive():
            self._draw_enemy_status(enemy, self.w - 296, 8)

    def _draw_enemy_status(self, enemy, x, y):
        """Gegner-Status-Block oben rechts"""
        max_w = self.w - x - 10
        if enemy.is_boss:
            pulse = int(25 * abs(math.sin(self._anim_t * 2)))
            c = (200 + min(55, pulse), 60, 60)
        elif enemy.is_elite:
            c = ACCENT_SOFT
        else:
            c = _lighten(enemy.color, 0.4)

        prefix = "👑 " if enemy.is_boss else ""
        name_str = prefix + enemy.name
        name_txt = self.font_small.render(name_str, True, c)
        while name_txt.get_width() > max_w and len(name_str) > len(prefix) + 4:
            name_str = name_str[:-1]
            name_txt = self.font_small.render(name_str + "…", True, c)
        self.screen.blit(name_txt, (x, y))

        # HP-Bar
        bar_w = min(280, max_w)
        self._bar(x, y + 22, bar_w, 15, enemy.hp / enemy.max_hp, HP_RED, radius=7)
        hp_txt = self.font_tiny.render(f"{enemy.hp}/{enemy.max_hp}", True, WHITE)
        self.screen.blit(hp_txt, (x + bar_w // 2 - hp_txt.get_width() // 2, y + 23))

        info = f"🛡 {enemy.armor}   ·   {enemy.get_intent_text()}"
        intent_txt = self.font_tiny.render(info, True, INK_DIM)
        while intent_txt.get_width() > max_w and len(info) > 6:
            info = info[:-1]
            intent_txt = self.font_tiny.render(info + "…", True, INK_DIM)
        self.screen.blit(intent_txt, (x, y + 40))

    def draw_damage_preview(self, enemy, dmg):
        """Zeigt den voraussichtlichen Schaden als helles Geist-Segment auf der Gegner-HP-Leiste"""
        x = self.w - 296
        bx, by, bh = x, 30, 15
        bw = min(280, self.w - x - 10)
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
        bx, by, bw, bh = 14, 14, 210, 20
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
        """Vertikale Reliktleiste mit Hover-Tooltip"""
        if not player.relics:
            return
        mx, my = pygame.mouse.get_pos()
        chip = 34
        gap = 6
        hovered = None
        for i, relic in enumerate(player.relics):
            ry = y + i * (chip + gap)
            rect = pygame.Rect(x, ry, chip, chip)
            hot = rect.collidepoint(mx, my)
            col_bg = (50, 40, 20) if hot else (34, 28, 50)
            border = ACCENT if hot else PANEL_LINE
            pygame.draw.rect(self.screen, col_bg, rect, border_radius=9)
            pygame.draw.rect(self.screen, border, rect, 2, border_radius=9)
            spr = assets.fit("relics", relic.get("id"), chip - 6, chip - 6)
            if spr:
                self.screen.blit(spr, (x + chip // 2 - spr.get_width() // 2,
                                       ry + chip // 2 - spr.get_height() // 2))
            else:
                em = self.font_medium.render(relic["emoji"], True, WHITE)
                self.screen.blit(em, (x + chip // 2 - em.get_width() // 2,
                                      ry + chip // 2 - em.get_height() // 2))
            if hot:
                hovered = relic
        if hovered:
            self._relic_tooltip(hovered, x + chip + 10, my)

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
        y = 232  # in der (während des Zuges leeren) Slot-Zone, über dem Log
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

        if enemy.burn > 0:
            self._text(f"🔥×{enemy.burn}", self.font_small, ORANGE, body_x - 18, body_y - 84)
        if enemy.weakened > 0:
            self._text(f"😵 {enemy.weakened}", self.font_tiny, PURPLE, body_x + 24, body_y - 84)

    # ═══════════════════════════════════════════════
    # HANDKARTEN
    # ═══════════════════════════════════════════════

    def draw_hand(self, hand, selected_card=None, hovered_idx=None):
        if not hand:
            return []
        card_w, card_h = 108, 146
        total_w = len(hand) * (card_w + 10)
        start_x = self.w // 2 - total_w // 2
        card_y = self.h - card_h - 8
        rects = []
        # zuerst nicht-gehoverte, dann gehoverte (oben drauf)
        order = [i for i in range(len(hand)) if i != hovered_idx]
        if hovered_idx is not None and hovered_idx < len(hand):
            order.append(hovered_idx)
        rects = [None] * len(hand)
        for i in range(len(hand)):
            cx = start_x + i * (card_w + 10)
            rects[i] = pygame.Rect(cx, card_y, card_w, card_h)
        for i in order:
            card = hand[i]
            lift = 24 if hovered_idx == i else (30 if selected_card == card else 0)
            cx = start_x + i * (card_w + 10)
            rect = pygame.Rect(cx, card_y - lift, card_w, card_h)
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

        # Karten-Korpus (dunkler Verlauf, leicht in Kartenfarbe getönt)
        tint_top = _lerp_color(CARD_BG, card.color, 0.16)
        tint_bot = _darken(CARD_BG, 0.25)
        body = self._panel_surface(w, h, 12, tint_top, tint_bot,
                                   rarity_col if active else CARD_BORDER, 2)
        self.screen.blit(body, (x, y))

        if active:
            glow = pygame.Surface((w + 12, h + 12), pygame.SRCALPHA)
            pygame.draw.rect(glow, (*rarity_col, 70), (0, 0, w + 12, h + 12), 4, border_radius=14)
            self.screen.blit(glow, (x - 6, y - 6))

        # Typ-Akzentleiste oben
        pygame.draw.rect(self.screen, card.color, (x + 8, y + 7, w - 16, 5), border_radius=3)

        # Kostenbadge
        cost_col = CYAN if card.cost == 0 else ACCENT
        pygame.draw.circle(self.screen, _darken(cost_col, 0.55), (x + 18, y + 28), 14)
        pygame.draw.circle(self.screen, cost_col, (x + 18, y + 28), 14, 2)
        ct = self.font_small.render(str(card.cost), True, WHITE)
        self.screen.blit(ct, (x + 18 - ct.get_width() // 2, y + 28 - ct.get_height() // 2))

        # Typ-Icon oben rechts
        self._text(card.get_type_icon(), self.font_small, card.color, x + w - 10, y + 19, right=True)

        # Name
        name_lines = self._wrap_text(card.name, self.font_small, w - 14)
        for li, line in enumerate(name_lines[:2]):
            self._text(line, self.font_small, INK, x + 8, y + 44 + li * 16)

        # Trennlinie
        pygame.draw.line(self.screen, (*CARD_BORDER, 180), (x + 8, y + 78), (x + w - 8, y + 78))

        # Wert
        if card.damage > 0:
            self._text(f"⚔ {card.damage}", self.font_medium, _lighten(RED, 0.25), x + w // 2, y + 82, center=True)
        elif card.block > 0:
            self._text(f"🛡 {card.block}", self.font_medium, _lighten(BLUE, 0.2), x + w // 2, y + 82, center=True)
        elif card.heal > 0:
            self._text(f"💚 {card.heal}", self.font_medium, _lighten(GREEN, 0.2), x + w // 2, y + 82, center=True)
        else:
            icon = "💀" if card.type == "curse" else "✨"
            self._text(icon, self.font_medium, PURPLE, x + w // 2, y + 82, center=True)

        # Marker: upgraded / exhaust
        if getattr(card, "upgraded", False):
            self._text("✦", self.font_small, ACCENT, x + w - 12, y + 44, right=True)
        if getattr(card, "exhaust", False):
            self._text("♻", self.font_tiny, ORANGE, x + w - 12, y + 62, right=True)

        # Tooltip
        self._draw_fitted_tooltip(card.tooltip, x + 6, y + 104, w - 12, y + h - 6 - (y + 104))

    def _draw_fitted_tooltip(self, text, x, y, w, h):
        candidates = [(self.font_tiny, 13), (self._font_micro, 11), (self._font_nano, 9)]
        for font, line_h in candidates:
            lines = self._wrap_text(text, font, w)
            if len(lines) * line_h <= h:
                for li, line in enumerate(lines):
                    self._text(line, font, INK_DIM, x, y + li * line_h)
                return
        font, line_h = candidates[-1]
        lines = self._wrap_text(text, font, w)
        max_lines = max(1, h // line_h)
        for li, line in enumerate(lines[:max_lines]):
            self._text(line, font, INK_DIM, x, y + li * line_h)

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
        self._panel((x, y, w, h), radius=12)
        max_lines = (h - 24) // 15
        total = len(log_entries)
        end = max(max_lines, total - scroll)
        entries = log_entries[max(0, end - max_lines):end]

        old_clip = self.screen.get_clip()
        self.screen.set_clip(pygame.Rect(x, y, w, h))

        hdr = "KAMPFLOG  ·  Mausrad scrollt" if total > max_lines else "KAMPFLOG"
        self._text(hdr, self.font_tiny, _darken(ACCENT, 0.1), x + 12, y + 6)
        pygame.draw.line(self.screen, (*PANEL_LINE, 120), (x + 10, y + 22), (x + w - 10, y + 22))

        for i, entry in enumerate(entries):
            newest = (i == len(entries) - 1) and scroll == 0
            ratio = (i + 1) / len(entries) if entries else 1
            color = CYAN if newest else _lerp_color(INK_FAINT, INK, ratio)
            self._text(entry, self.font_tiny, color, x + 12, y + 28 + i * 15)

        if scroll > 0:
            self._text("▲ älter", self.font_tiny, ACCENT, x + w - 60, y + 6)
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

        hovered = rect.collidepoint(pygame.mouse.get_pos())
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

    def button_hovered(self, x, y, w, h):
        mx, my = pygame.mouse.get_pos()
        return x <= mx <= x + w and y <= my <= y + h

    # ═══════════════════════════════════════════════
    # OVERLAYS
    # ═══════════════════════════════════════════════

    def _dim(self, alpha=180):
        overlay = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, alpha))
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
            hov = pygame.Rect(cx, cy, card_w, 210).collidepoint(pygame.mouse.get_pos())
            rect = pygame.Rect(cx, cy - (8 if hov else 0), card_w, 210)
            card_rects.append(pygame.Rect(cx, cy, card_w, 210))
            self._draw_card(card, rect, hovered=hov)

        skip_rect = pygame.Rect(self.w // 2 - 90, py + ph - 58, 180, 42)
        self.draw_button("Überspringen ➡", skip_rect.x, skip_rect.y, skip_rect.w, skip_rect.h,
                         color=GREY_DARK, text_color=WHITE)
        return card_rects, skip_rect

    # ═══════════════════════════════════════════════
    # EVENT-SCREEN
    # ═══════════════════════════════════════════════

    def draw_event(self, event, resolved, result_text, hovered_idx):
        self.draw_background()
        pw, ph = 720, 580
        px, py = self.w // 2 - pw // 2, self.h // 2 - ph // 2
        self._panel((px, py, pw, ph), radius=18, border=PURPLE, border_w=3)

        self._text(event["emoji"], self.font_huge, WHITE, self.w // 2, py + 22, center=True)
        self._text(event["title"], self.font_h1, _lighten(PURPLE, 0.4),
                   self.w // 2, py + 78, center=True, shadow=True)

        # Beschreibung (umgebrochen, zentriert)
        desc_lines = self._wrap_text(event["text"], self.font_small, pw - 100)
        for i, line in enumerate(desc_lines):
            self._text(line, self.font_small, INK_DIM, self.w // 2, py + 124 + i * 20, center=True)

        option_rects = []
        continue_rect = None
        oy = py + 124 + len(desc_lines) * 20 + 20

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
            self.draw_button("Weiter ➡", continue_rect.x, continue_rect.y,
                             continue_rect.w, continue_rect.h, color=GREEN, pulsing=True)
        return option_rects, continue_rect

    # ═══════════════════════════════════════════════
    # GAME OVER / SIEG
    # ═══════════════════════════════════════════════

    def draw_game_over(self, player, floor_num, score=0, rank=None):
        self.draw_background()
        self._dim(150)
        self._text("💀  DU BIST TOT  💀", self.font_huge, RED, self.w // 2, 80, center=True, shadow=True)

        pw = 460
        self._panel((self.w // 2 - pw // 2, 150, pw, 70), radius=14, border=ACCENT)
        self._text(f"PUNKTE: {score:,}".replace(",", "."), self.font_h1, ACCENT,
                   self.w // 2, 162, center=True)
        if rank == 1:
            self._text("🥇 NEUER REKORD!", self.font_small, ACCENT_SOFT, self.w // 2, 196, center=True)
        elif rank:
            self._text(f"Platz {rank} in der Bestenliste", self.font_small, CYAN, self.w // 2, 196, center=True)

        msgs = [
            f"🏯 Etage {floor_num} erreicht",
            f"🐔 Hühner beschworen: {player.chickens_summoned}",
            f"💰 Gold verdient: {player.gold_earned}",
            f"⚔ Schaden verursacht: {player.damage_dealt}",
            f"🎰 Slots gedreht: {player.slots_spun}",
            f"💠 Relikte gesammelt: {len(player.relics)}",
        ]
        for i, msg in enumerate(msgs):
            self._text(msg, self.font_medium, INK, self.w // 2, 250 + i * 34, center=True)

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

        self.draw_button("🏆 Bestenliste", self.w // 2 - 100, self.h - 122, 200, 46,
                         color=PURPLE, text_color=WHITE)
        self._text("R = nochmal   ·   ESC = Beenden", self.font_small, INK_FAINT,
                   self.w // 2, self.h - 56, center=True)

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
        tu = layout["tutorial"]
        self.draw_button("📖 Tutorial", tu.x, tu.y, tu.w, tu.h, color=CYAN, text_color=BLACK)
        op = layout["options"]
        self.draw_button("⚙ Optionen", op.x, op.y, op.w, op.h, color=BLUE, text_color=WHITE)
        sc = layout["scores"]
        self.draw_button("🏆 Bestenliste", sc.x, sc.y, sc.w, sc.h, color=PURPLE, text_color=WHITE)

        cl = layout.get("changelog")
        if cl:
            hot = cl.collidepoint(pygame.mouse.get_pos())
            self._chip("🆕 Was ist neu?", self.font_small, cl.x, cl.y,
                       text_col=ACCENT_SOFT if hot else INK_DIM, fill=(*PANEL_FILL, 200),
                       border=ACCENT if hot else PANEL_LINE)

        self._text(f"v{GAME_VERSION}", self.font_tiny, INK_FAINT, self.w - 14, self.h - 22, right=True)

    def draw_changelog(self, entries):
        """Kompakte 'Was ist neu' – eine Zeile pro Version."""
        self.draw_background()
        self._dim(150)
        pw, ph = 640, 440
        px, py = self.w // 2 - pw // 2, self.h // 2 - ph // 2 - 10
        self._panel((px, py, pw, ph), radius=18, border=ACCENT, border_w=3)
        self._text("🆕  WAS IST NEU", self.font_huge, ACCENT, self.w // 2, py + 18, center=True, shadow=True)

        y = py + 84
        for i, (ver, line) in enumerate(entries[:7]):
            newest = (i == 0)
            # Versions-Pille
            vcol = ACCENT if newest else INK_DIM
            self._chip(f"v{ver}", self.font_small, px + 28, y,
                       text_col=BLACK if newest else INK, fill=(255, 198, 64, 255) if newest else (*GREY_DARK, 220))
            self._text(line, self.font_small, INK if newest else INK_DIM, px + 130, y + 4)
            y += 46

        back = pygame.Rect(self.w // 2 - 100, self.h - 62, 200, 44)
        self.draw_button("⬅ Zurück", back.x, back.y, back.w, back.h, color=ACCENT, text_color=BLACK)
        return back

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

    def draw_map(self, gamemap, current, available, hovered, player, act, message=""):
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

    def _map_legend(self):
        items = [("⚔", "Kampf"), ("⭐", "Elite"), ("❓", "Event"),
                 ("🏪", "Shop"), ("🔥", "Rast"), ("💠", "Schatz"), ("👑", "Boss")]
        x = 16
        y = self.h - 30
        for icon, label in items:
            s = f"{icon} {label}"
            self._text(s, self.font_tiny, INK_FAINT, x, y)
            x += self.font_tiny.size(s)[0] + 16

    def draw_rest(self, player, layout):
        """Lagerfeuer: Heilen oder Karte aufwerten"""
        self.draw_background()
        self._dim(120)
        self._text("🔥  LAGERFEUER", self.font_huge, ORANGE, self.w // 2, 70, center=True, shadow=True)
        self._text("Ein Moment der Ruhe. Nutze ihn weise.", self.font_small, INK_DIM,
                   self.w // 2, 132, center=True)
        mouse = pygame.mouse.get_pos()

        for keyname, title, emoji, desc, col in [
            ("heal", "Ausruhen", "❤", f"Heile 30% deiner Max-HP\n(+{int(player.max_hp*0.3)} HP)", GREEN),
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
        self.draw_button("➡ Weiter (ohne Rast)", lv.x, lv.y, lv.w, lv.h,
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

        tlabels = {"fullscreen": "🖥 Vollbild", "shake": "📳 Screen-Shake", "particles": "✨ Partikel"}
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

        b = layout["back"]
        self.draw_button("⬅ Zurück", b.x, b.y, b.w, b.h, color=ACCENT, text_color=BLACK)
        d = layout["defaults"]
        self.draw_button("↺ Standard", d.x, d.y, d.w, d.h, color=GREY_DARK, text_color=WHITE)
        self._text("Tipp: [M] schaltet den Ton schnell stumm.", self.font_tiny, INK_FAINT,
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
                "Karte hovern zeigt den Schaden vorab. Dann 'Slot drehen'.",
            ]),
            ("🎰  SLOTS & GEGNER", ACCENT, [
                "Slot drehen: gleiche Symbole = starke Kombos, 🍀 hilft.",
                "Danach greift der Gegner an (seine Absicht steht oben rechts).",
                "Gegner haben Tricks: Gold klauen, Gift, Slot blockieren …",
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

        back_rect = pygame.Rect(self.w // 2 - 100, self.h - 62, 200, 44)
        self.draw_button("⬅ Zurück zum Menü", back_rect.x, back_rect.y, back_rect.w, back_rect.h,
                         color=ACCENT, text_color=BLACK)
        return back_rect

    # ═══════════════════════════════════════════════
    # SHOP
    # ═══════════════════════════════════════════════

    def draw_shop(self, items, player, message=""):
        self.draw_background()
        self._text("🏪  DUBIOSER LADEN  🏪", self.font_huge, ACCENT, self.w // 2, 18, center=True, shadow=True)
        self._text("Der Händler riecht nach Bier und schlechten Entscheidungen.",
                   self.font_small, INK_DIM, self.w // 2, 74, center=True)
        self._chip(f"💰 Dein Gold: {player.gold}", self.font_title, self.w // 2 - 90, 100,
                   text_col=ACCENT, fill=(60, 45, 12, 200))

        item_rects = []
        item_w, item_h = 196, 156
        spacing = 16
        cols = len(items)
        total_w = cols * item_w + (cols - 1) * spacing
        start_x = self.w // 2 - total_w // 2
        item_y = 150
        mouse = pygame.mouse.get_pos()

        for i, item in enumerate(items):
            ix = start_x + i * (item_w + spacing)
            rect = pygame.Rect(ix, item_y, item_w, item_h)
            item_rects.append((rect, item))
            affordable = player.gold >= item["cost"]
            hovered = rect.collidepoint(mouse)
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
        for li, line in enumerate(["Einsatz: 25 Gold", "Gewinne bis zu 10×!", "(Meist verlierst du. Aber hey.)"]):
            self._text(line, self._font_micro, INK_DIM, gamble_rect.centerx, gamble_rect.y + 54 + li * 16, center=True)
        can_gamble = player.gold >= 25
        self.draw_button("🎲 DREHEN (25💰)", gamble_rect.x + 55, gamble_rect.y + 116, 200, 40,
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
        self.draw_button("Weiter zur nächsten Etage ➡", leave_rect.x, leave_rect.y,
                         leave_rect.w, leave_rect.h, color=GREEN, text_color=BLACK, pulsing=True)
        return item_rects, gamble_rect, leave_rect

    def draw_card_grid(self, player, title, accent, only_upgradeable=False):
        """Karten-Auswahlraster (Verbrennen oder Aufwerten). Gibt [(rect, card)] zurück."""
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
        mouse = pygame.mouse.get_pos()

        for i, card in enumerate(all_cards):
            row, col = i // per_row, i % per_row
            cx = start_x + col * (card_w + spacing)
            cy = start_y + row * (card_h + spacing)
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

        self.draw_button("Abbrechen", self.w // 2 - 80, self.h - 70, 160, 42,
                         color=GREY_DARK, text_color=WHITE)
        return rects

    # Rückwärtskompatibilität (falls noch referenziert)
    def draw_card_removal(self, player):
        return self.draw_card_grid(player, "🔥 Welche Karte verbrennen?", ORANGE)

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
        self.draw_button("⬅ Zurück", back_rect.x, back_rect.y, back_rect.w, back_rect.h,
                         color=ACCENT, text_color=BLACK)
        return back_rect
