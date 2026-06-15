"""Konstanten und Konfiguration für das gesamte Spiel"""

# Version (rein informativ; Spielstände sind versionsunabhängig gültig)
GAME_VERSION = "1.15.0"

# Speicherstand-Datei (laufender Run)
SAVE_FILE = "savegame.json"

# Kompakte In-Game-Changelist (neueste oben, EINE kurze Zeile pro Version)
CHANGELOG = [
    ("1.15.0", "Schwerer & runder: Gegner skalieren (HP/Block/Ruestung), UI-Fixes (Relikte, Status, Karten)"),
    ("1.14.0", "NEUER SPIELMODUS: Slot-Modus (Balatro-Style) - bau deinen Automaten, knack die Ziele!"),
    ("1.13.0", "Musik pro Akt, Schwierigkeitsgrade, Schnell-Modus, Autosave, 8 neue Erfolge"),
    ("1.12.0", "RIESEN-UPDATE 2: 22 Karten, 12 Relikte, 9 Gegner, 3 Akte, 6 Status + Auto-Update"),
    ("1.11.0", "Neue Musik je Situation (Menü/Karte/Kampf/Boss) + Tastatursteuerung"),
    ("1.10.3", "Pfade auf der Karte kreuzen sich nicht mehr"),
    ("1.10.2", "Im Kampf wird jetzt dein Klassen-Portrait als Avatar gezeigt"),
    ("1.10.1", "Spielstände bleiben jetzt IMMER gültig – kein Save-Verlust durch Updates"),
    ("1.10.0", "RIESEN-UPDATE: 14 Karten, 9 Relikte, 7 Gegner (mit Sprites) + Nerf"),
    ("1.9.1", "Akt-Hintergruende, Klassen-Portraits, 5 neue Gegner & viele Icons"),
    ("1.9.0", "START-KLASSEN! Ritter, Hochstapler, Hexe - je eigenes Deck & Relikt"),
    ("1.8.5", "Akt-Themen: jeder Akt eigene Gegner-Auswahl, Name & Boss"),
    ("1.8.4", "Slot-Synergien: Symbol-Paare & Misch-Kombos geben Extra-Boni"),
    ("1.8.3", "Effekt-Icons auf Karten + echter Slot-Automat-Rahmen"),
    ("1.8.2", "Echte Pixel-Art-Sprites: 6 neue Gegner + Casino-Event"),
    ("1.8.1", "Tages-Challenge mit Streak · Meta-Unlocks · Casino-Event · Run-Stats"),
    ("1.8.0", "GROSSES CONTENT-UPDATE: Gift & neue Status, 8 Karten, 6 Gegner, 6 Relikte"),
    ("1.7.5", "16 Erfolge! Dauerhaft über Runs, mit Einblendung beim Freischalten"),
    ("1.7.4", "Verspotten gibt −2 Stärke · Deck-Scrollen · weniger Deko-Emojis"),
    ("1.7.3", "Weniger RAM-Verbrauch (~−14 MB) · flüssigeres Rendern"),
    ("1.7.2", "Glücksrad fairer (Haus gewinnt) · kein Weiterdrehen nach Kill"),
    ("1.7.1", "Karten-Beschreibungen jetzt deutlich besser lesbar"),
    ("1.7.0", "Highscores speichern · Kampf-UI neu · Bosse fairer · Block-Fix"),
    ("1.6.5", "'Akt geschafft!'-Bildschirm nach jedem Boss (geht endlos weiter)"),
    ("1.6.4", "Karten-Rahmen, Spieler-Avatar, Sieg/Niederlage-Bilder, App-Icon"),
    ("1.6.3", "Fairer: mehr Shops/Heilung, sanftere Skalierung + Event-Bilder"),
    ("1.6.2", "Fix: Slot-Softlock (Glücksprüfer); Shop-Items nur 1x/Besuch"),
    ("1.6.1", "Vorschau: Heilung & eingehender Schaden auf der HP-Leiste"),
    ("1.6.0", "In-Game 'Was ist neu' – diese Übersicht hier"),
    ("1.5.0", "Optionsmenü: Lautstärke, Vollbild & Effekte einstellbar"),
    ("1.4.0", "Pixel-Art-Grafik: Gegner, Slot-Symbole, Logo & Kulisse"),
    ("1.3.0", "Gegner & Bosse mit eigenen Spezialfähigkeiten"),
    ("1.2.0", "Pfad-Karte mit Akten – wähle deinen Weg"),
    ("1.1.0", "Sound & Musik, Effekte und Schadens-Vorschau"),
    ("1.0.0", "Erste Vollversion: Speichern & Fortsetzen"),
]

# Farben (Casino-Stil: dunkel, Gold, Rot)
BLACK       = (0, 0, 0)
WHITE       = (255, 255, 255)
DARK_BG     = (15, 10, 25)
DARKER_BG   = (8, 5, 15)
GOLD        = (255, 200, 50)
GOLD_DARK   = (180, 140, 30)
RED         = (220, 50, 50)
RED_DARK    = (150, 30, 30)
GREEN       = (50, 200, 80)
GREEN_DARK  = (30, 120, 50)
BLUE        = (80, 140, 220)
BLUE_DARK   = (40, 80, 150)
PURPLE      = (160, 80, 220)
PURPLE_DARK = (90, 40, 140)
ORANGE      = (230, 140, 30)
CYAN        = (50, 220, 220)
GREY        = (120, 120, 130)
GREY_DARK   = (60, 60, 70)
CARD_BG     = (30, 22, 50)
CARD_BORDER = (100, 80, 140)
SLOT_BG     = (20, 15, 35)
SLOT_REEL   = (40, 30, 60)
HP_RED      = (220, 60, 60)
HP_GREEN    = (60, 200, 80)
ENEMY_COLOR = (180, 60, 60)
PANEL_BG    = (20, 15, 35, 200)

# ─── Modernes UI: erweiterte Palette ───
BG_TOP      = (24, 18, 42)    # Hintergrund-Gradient oben
BG_BOTTOM   = (10, 7, 20)     # Hintergrund-Gradient unten
PANEL_FILL  = (28, 22, 46)    # Glas-Panel Füllung
PANEL_FILL2 = (36, 28, 58)    # Glas-Panel oberer Verlauf
PANEL_LINE  = (78, 64, 116)   # Panel-Rahmen
PANEL_HI    = (120, 104, 168) # Panel-Highlight (oben)
INK         = (236, 232, 246) # Haupt-Textfarbe (weiches Weiß)
INK_DIM     = (168, 160, 192) # gedämpfter Text
INK_FAINT   = (110, 104, 132) # sehr dezenter Text
ACCENT      = (255, 198, 64)  # Gold-Akzent (primär)
ACCENT_SOFT = (255, 224, 150) # helles Gold
SHADOW      = (0, 0, 0)       # Schattenfarbe (mit Alpha verwendet)
CURSE_COL   = (150, 60, 170)  # Fluch-Karten

# Bildschirm
SCREEN_W = 1200
SCREEN_H = 800

# Spieler-Startwerte
PLAYER_MAX_HP = 100
PLAYER_START_GOLD = 50
PLAYER_HAND_SIZE = 5
PLAYER_ENERGY_PER_TURN = 3

# Wie viele Karten man pro Runde NACHZIEHT (behält ungespielte Karten)
PLAYER_DRAW_PER_TURN = 3
PLAYER_MAX_HAND = 7   # Obergrenze, damit man nicht unendlich hortet

# Highscore-Datei
HIGHSCORE_FILE = "highscores.json"
MAX_HIGHSCORES = 10

# Shop-Angebote (zwischen den Etagen)
# kind: was passiert. cost: Gold-Preis. Manche werden dynamisch generiert.
SHOP_FIXED_ITEMS = [
    {"id": "heal_full",  "name": "Vollheilung",      "emoji": "❤️",  "cost": 60,
     "desc": "Heile auf Maximum. Spüre die Lebensfreude."},
    {"id": "heal_half",  "name": "Verband",          "emoji": "🩹", "cost": 25,
     "desc": "Heile 30 HP. Klebt gut."},
    {"id": "max_hp",     "name": "Protein-Shake",    "emoji": "💪", "cost": 45,
     "desc": "+15 Max HP dauerhaft. Schmeckt nach Banane."},
    {"id": "strength",   "name": "Krafttrank",       "emoji": "⚡", "cost": 40,
     "desc": "+2 Stärke für den Rest des Runs."},
    {"id": "max_energy", "name": "Energy Drink",     "emoji": "🔋", "cost": 70,
     "desc": "+1 Max Energie dauerhaft. Herzrasen inklusive."},
    {"id": "remove_card","name": "Karte verbrennen", "emoji": "🔥", "cost": 35,
     "desc": "Entferne eine schwache Karte aus dem Deck."},
    {"id": "extra_spin", "name": "Glücks-Token",     "emoji": "🎰", "cost": 30,
     "desc": "+2 Glücksrunden für bessere Slots."},
]

# Slot-Symbole
SLOT_SYMBOLS = [
    {"emoji": "💀", "name": "SKULL",    "weight": 15},
    {"emoji": "🍀", "name": "CLOVER",   "weight": 10},
    {"emoji": "💰", "name": "MONEY",    "weight": 15},
    {"emoji": "❤️",  "name": "HEART",    "weight": 12},
    {"emoji": "🎲", "name": "DICE",     "weight": 12},
    {"emoji": "🔥", "name": "FIRE",     "weight": 10},
    {"emoji": "🐔", "name": "CHICKEN",  "weight": 8},
    {"emoji": "⭐", "name": "STAR",     "weight": 10},
    {"emoji": "💣", "name": "BOMB",     "weight": 6},
    {"emoji": "🌀", "name": "VORTEX",   "weight": 7},
    {"emoji": "🍺", "name": "BEER",     "weight": 8},
    {"emoji": "👑", "name": "CROWN",    "weight": 5},
    # ─── Neue Symbole ───
    {"emoji": "⚡", "name": "LIGHTNING", "weight": 8},   # Sofortschaden + Energie
    {"emoji": "🛡️",  "name": "SHIELD",   "weight": 8},   # Block für nächste Gegnerrunde
    {"emoji": "🎯", "name": "TARGET",   "weight": 7},   # Garantierter Krit
    {"emoji": "🍒", "name": "CHERRY",   "weight": 9},   # Kleiner Allrounder
    {"emoji": "💎", "name": "DIAMOND",  "weight": 4},   # Selten, viel Gold + Buff
    {"emoji": "🐍", "name": "SNAKE",    "weight": 6},   # Gift / riskant
    {"emoji": "🌙", "name": "MOON",     "weight": 5},   # Heilung skaliert mit fehlendem HP
    {"emoji": "🤡", "name": "CLOWN",    "weight": 5},   # Chaos, eindeutig nervig
]

# Gegner-Typen
ENEMY_TYPES = [
    {
        "name": "Schluffiger Goblin",
        "asset": "goblin",
        "hp": 30, "max_hp": 30,
        "damage": 6, "armor": 0,
        "gold_reward": (8, 15),
        "color": GREEN_DARK,
        "tooltip": "Riecht nach Zwiebeln. Kämpft trotzdem.",
        "tier": 1
    },
    {
        "name": "Betrunkener Ritter",
        "asset": "ritter",
        "hp": 45, "max_hp": 45,
        "damage": 10, "armor": 3,
        "gold_reward": (12, 20),
        "color": BLUE_DARK,
        "tooltip": "War mal ehrenhaft. Dann kam das Bier. Schlägt wuchtig – oder stolpert.",
        "tier": 1,
        "mechanic": "reckless"
    },
    {
        "name": "Pestratte",
        "asset": "pestratte",
        "hp": 28, "max_hp": 28,
        "damage": 5, "armor": 0,
        "gold_reward": (8, 14),
        "color": GREEN_DARK,
        "tooltip": "Beißt und verseucht. Ihre Angriffe vergiften dich (Burn).",
        "tier": 1,
        "mechanic": "chili"
    },
    {
        "name": "Steuerprüfer",
        "asset": "steuerpruefer",
        "hp": 40, "max_hp": 40,
        "damage": 8, "armor": 2,
        "gold_reward": (15, 25),
        "color": GREY,
        "tooltip": "Stiehlt dein Gold beim Angriff. Nennt es 'Abgaben'.",
        "tier": 1,
        "mechanic": "gold_thief"
    },
    {
        "name": "Philosophischer Lich",
        "asset": "lich",
        "hp": 60, "max_hp": 60,
        "damage": 14, "armor": 1,
        "gold_reward": (18, 28),
        "color": PURPLE_DARK,
        "tooltip": "Überlebt seinen ersten Tod ('Was ist überhaupt Tod?').",
        "tier": 2,
        "mechanic": "undying"
    },
    {
        "name": "Wütender Koch",
        "asset": "koch",
        "hp": 55, "max_hp": 55,
        "damage": 12, "armor": 4,
        "gold_reward": (16, 24),
        "color": ORANGE,
        "tooltip": "Zu viel Chili gegessen. Seine Hiebe setzen dich in Brand (Burn).",
        "tier": 2,
        "mechanic": "chili"
    },
    {
        "name": "Vampir-Croupier",
        "asset": "croupier",
        "hp": 52, "max_hp": 52,
        "damage": 11, "armor": 2,
        "gold_reward": (18, 28),
        "color": RED_DARK,
        "tooltip": "Das Haus gewinnt immer. Heilt sich an deinem Blut, wenn er trifft.",
        "tier": 2,
        "mechanic": "siphon"
    },
    {
        "name": "Slot-Maschinendämon",
        "asset": "slot_daemon",
        "hp": 70, "max_hp": 70,
        "damage": 16, "armor": 2,
        "gold_reward": (22, 35),
        "color": GOLD_DARK,
        "tooltip": "Er IST der Spielautomat. Blockiert manchmal deine Drehung.",
        "tier": 2,
        "mechanic": "slot_jammer"
    },
    {
        "name": "DER GROSSE HÜHNERKÖNIG",
        "asset": "boss_huhnerkoenig",
        "hp": 100, "max_hp": 100,
        "damage": 12, "armor": 2,
        "gold_reward": (40, 60),
        "color": (255, 220, 50),
        "tooltip": "BOSS: Wird jede Runde gefährlicher – legt Eier, ruft sein Gefolge.",
        "tier": 3,
        "is_boss": True,
        "mechanic": "chicken_army"
    },
    {
        "name": "Oberster Glücksprüfer",
        "asset": "boss_glueckspruefer",
        "hp": 120, "max_hp": 120,
        "damage": 14, "armor": 3,
        "gold_reward": (50, 80),
        "color": PURPLE,
        "tooltip": "BOSS: Löscht dein Glück, blockiert den Automaten und saugt Leben.",
        "tier": 3,
        "is_boss": True,
        "mechanic": "rig_slots"
    },
    # ─── Neue Gegner (v1.8.0) ───
    {
        "name": "Sumpfschleim",
        "asset": "schleim",
        "hp": 26, "max_hp": 26,
        "damage": 4, "armor": 0,
        "gold_reward": (8, 14),
        "color": GREEN_DARK,
        "tooltip": "Glibbert bedrohlich. Seine Treffer vergiften dich (Gift tickt jede Runde).",
        "tier": 1,
        "mechanic": "venom"
    },
    {
        "name": "Kneipenschläger",
        "asset": "schlaeger",
        "hp": 38, "max_hp": 38,
        "damage": 7, "armor": 0,
        "gold_reward": (10, 16),
        "color": RED_DARK,
        "tooltip": "Wird WÜTEND, wenn er blutet: unter halben HP schlägt er härter zu.",
        "tier": 1,
        "mechanic": "enrage"
    },
    {
        "name": "Pilzkönigin",
        "asset": "pilzkoenigin",
        "hp": 58, "max_hp": 58,
        "damage": 9, "armor": 1,
        "gold_reward": (18, 26),
        "color": PURPLE_DARK,
        "tooltip": "Verströmt jede Runde Sporen: +2 Gift auf dich, ganz ohne Angriff.",
        "tier": 2,
        "mechanic": "spores"
    },
    {
        "name": "Verfluchter Spiegel",
        "asset": "spiegel",
        "hp": 64, "max_hp": 64,
        "damage": 10, "armor": 3,
        "gold_reward": (20, 30),
        "color": GREY,
        "tooltip": "Zeigt dir dein schlechtestes Ich: legt dir manchmal Flüche ins Deck.",
        "tier": 2,
        "mechanic": "curse_gift"
    },
    {
        "name": "Glücksgeist",
        "asset": "gluecksgeist",
        "hp": 48, "max_hp": 48,
        "damage": 8, "armor": 0,
        "gold_reward": (16, 24),
        "color": CYAN,
        "tooltip": "Halb durchsichtig, ganz gemein: stiehlt deine Glücksrunden für sich.",
        "tier": 2,
        "mechanic": "luck_eater"
    },
    {
        "name": "MADAME FORTUNA",
        "asset": "boss_fortuna",
        "hp": 130, "max_hp": 130,
        "damage": 13, "armor": 2,
        "gold_reward": (50, 85),
        "color": (240, 90, 160),
        "tooltip": "BOSS: Dreht jede Runde ihr Schicksalsrad – Gift, Diebstahl, Heilung oder Doppelschlag.",
        "tier": 3,
        "is_boss": True,
        "mechanic": "fortuna"
    },
    # ─── Neue Akt-Gegner (v1.9.1) ───
    {
        "name": "Falschspieler",
        "asset": "falschspieler",
        "hp": 50, "max_hp": 50,
        "damage": 9, "armor": 1,
        "gold_reward": (18, 28),
        "color": RED_DARK,
        "tooltip": "Hat immer ein Ass im Ärmel – und klaut dir beim Angriff Gold.",
        "tier": 2,
        "mechanic": "gold_thief"
    },
    {
        "name": "Einarmiger Bandit",
        "asset": "einarmiger_bandit",
        "hp": 62, "max_hp": 62,
        "damage": 11, "armor": 3,
        "gold_reward": (20, 30),
        "color": GOLD_DARK,
        "tooltip": "Lebender Spielautomat. Blockiert gern deine Drehung.",
        "tier": 2,
        "mechanic": "slot_jammer"
    },
    {
        "name": "Geisterbraut",
        "asset": "geisterbraut",
        "hp": 54, "max_hp": 54,
        "damage": 10, "armor": 1,
        "gold_reward": (18, 28),
        "color": CYAN,
        "tooltip": "Weint um eine verlorene Liebe und saugt dir das Leben aus.",
        "tier": 2,
        "mechanic": "siphon"
    },
    {
        "name": "Knochenkoch",
        "asset": "knochenkoch",
        "hp": 58, "max_hp": 58,
        "damage": 10, "armor": 2,
        "gold_reward": (18, 27),
        "color": GREEN_DARK,
        "tooltip": "Sein verfluchter Eintopf vergiftet dich bei jedem Treffer.",
        "tier": 2,
        "mechanic": "venom"
    },
    {
        "name": "DER SENSENMANN",
        "asset": "boss_sensenmann",
        "hp": 135, "max_hp": 135,
        "damage": 14, "armor": 3,
        "gold_reward": (55, 90),
        "color": PURPLE,
        "tooltip": "BOSS: Croupier des Todes. Teilt das Schicksal aus – und betrügt den Tod selbst.",
        "tier": 3,
        "is_boss": True,
        "mechanic": "reaper"
    },
    # ─── Neue Gegner (v1.10.0) ───
    {
        "name": "Würfelgnom", "asset": "wuerfelgnom",
        "hp": 26, "max_hp": 26, "damage": 5, "armor": 0,
        "gold_reward": (9, 16), "color": ORANGE,
        "tooltip": "Wirft ständig Würfel. Mal trifft's dich, mal heilt es ihn.",
        "tier": 1, "mechanic": "gambler_foe"
    },
    {
        "name": "Bierbauch-Ork", "asset": "bierork",
        "hp": 44, "max_hp": 44, "damage": 9, "armor": 2,
        "gold_reward": (12, 20), "color": GREEN_DARK,
        "tooltip": "Schlägt wuchtig zu – oder rülpst und verfehlt komplett.",
        "tier": 1, "mechanic": "reckless"
    },
    {
        "name": "Roulette-Geist", "asset": "roulettegeist",
        "hp": 50, "max_hp": 50, "damage": 12, "armor": 1,
        "gold_reward": (18, 28), "color": RED,
        "tooltip": "Setzt alles auf eine Zahl: doppelter Schaden – oder gar keiner.",
        "tier": 2, "mechanic": "roulette_foe"
    },
    {
        "name": "Münzgolem", "asset": "muenzgolem",
        "hp": 70, "max_hp": 70, "damage": 9, "armor": 5,
        "gold_reward": (28, 40), "color": GOLD_DARK,
        "tooltip": "Aus purem Gold. Schwer zu knacken, aber lohnend.",
        "tier": 2
    },
    {
        "name": "Schattenkrähe", "asset": "schattenkraehe",
        "hp": 46, "max_hp": 46, "damage": 8, "armor": 0,
        "gold_reward": (16, 24), "color": PURPLE_DARK,
        "tooltip": "Ihre Krallen durchdringen Block (3 Schaden ignorieren Block).",
        "tier": 2, "mechanic": "pierce"
    },
    {
        "name": "Gruftwächter", "asset": "gruftwaechter",
        "hp": 66, "max_hp": 66, "damage": 11, "armor": 4,
        "gold_reward": (20, 30), "color": GREY,
        "tooltip": "Uralter Steinwächter. Dick gepanzert und unerbittlich.",
        "tier": 2
    },
    {
        "name": "DER BANKHALTER", "asset": "boss_bankhalter",
        "hp": 140, "max_hp": 140, "damage": 13, "armor": 3,
        "gold_reward": (60, 95), "color": GOLD,
        "tooltip": "BOSS: Das Haus persönlich. Je reicher du bist, desto härter schlägt er zu.",
        "tier": 3, "is_boss": True, "mechanic": "house_edge"
    },
    # ─── Neue Gegner (v1.12.0) für die neuen Akte ───
    # AKT 4 – Die Kanalisation (Gift/Seuche)
    {"name": "Riesenkanalratte", "asset": "kanalratte", "hp": 64, "max_hp": 64,
     "damage": 11, "armor": 1, "gold_reward": (20, 30), "color": GREEN_DARK,
     "tooltip": "So groß wie ein Hund, doppelt so eklig. Ihre Bisse vergiften.",
     "tier": 2, "mechanic": "venom"},
    {"name": "Seuchendoktor", "asset": "seuchendoktor", "hp": 70, "max_hp": 70,
     "damage": 10, "armor": 2, "gold_reward": (24, 34), "color": GREEN_DARK,
     "tooltip": "Heilt niemanden. Seine 'Behandlung' vergiftet und schwächt dich.",
     "tier": 3, "mechanic": "plague"},
    {"name": "DIE BRUTMUTTER", "asset": "boss_brutmutter", "hp": 150, "max_hp": 150,
     "damage": 12, "armor": 2, "gold_reward": (60, 95), "color": GREEN,
     "tooltip": "BOSS: Verseucht dich jede Runde mit immer mehr Gift. Lass sie nicht stapeln.",
     "tier": 3, "is_boss": True, "mechanic": "infest"},
    # AKT 5 – Der Frostpalast (Frost/Verwundbar)
    {"name": "Frostgolem", "asset": "frostgolem", "hp": 88, "max_hp": 88,
     "damage": 12, "armor": 6, "gold_reward": (26, 38), "color": CYAN,
     "tooltip": "Ein Koloss aus ewigem Eis. Schwer zu knacken.",
     "tier": 3},
    {"name": "Eishexe", "asset": "eishexe", "hp": 66, "max_hp": 66,
     "damage": 11, "armor": 2, "gold_reward": (24, 34), "color": BLUE,
     "tooltip": "Ihr eisiger Hauch macht dich verwundbar (du nimmst mehr Schaden).",
     "tier": 3, "mechanic": "chill"},
    {"name": "DER FROSTKÖNIG", "asset": "boss_frostkoenig", "hp": 160, "max_hp": 160,
     "damage": 15, "armor": 4, "gold_reward": (65, 100), "color": CYAN,
     "tooltip": "BOSS: Friert dich ein (verwundbar) und schlägt dann gnadenlos zu.",
     "tier": 3, "is_boss": True, "mechanic": "freeze"},
    # AKT 6 – Die Unterwelt (Feuer/Verhängnis)
    {"name": "Höllenhund", "asset": "hoellenhund", "hp": 72, "max_hp": 72,
     "damage": 13, "armor": 1, "gold_reward": (26, 38), "color": RED,
     "tooltip": "Drei Köpfe, dreifacher Geifer. Setzt dich in Brand.",
     "tier": 3, "mechanic": "chili"},
    {"name": "Qualdämon", "asset": "qualdaemon", "hp": 80, "max_hp": 80,
     "damage": 14, "armor": 2, "gold_reward": (28, 40), "color": RED_DARK,
     "tooltip": "Lebt vom Schmerz. Schlägt wuchtig – oder verschnauft kurz.",
     "tier": 3, "mechanic": "reckless"},
    {"name": "LUZIFER", "asset": "boss_luzifer", "hp": 175, "max_hp": 175,
     "damage": 16, "armor": 3, "gold_reward": (70, 110), "color": RED_DARK,
     "tooltip": "BOSS: Der Herr der Unterwelt. Sein Feuer wird jede Runde heißer.",
     "tier": 3, "is_boss": True, "mechanic": "infernal"},
]

# Karten-Pool
CARD_DEFINITIONS = [
    # ═══ ANGRIFF ═══
    {
        "name": "Fireball",
        "type": "attack",
        "cost": 2,
        "damage": 18,
        "color": RED,
        "tooltip": "Setzt Dinge in Brand. Manchmal die falschen.",
        "rarity": "common",
        "effect": "damage"
    },
    {
        "name": "Schneller Stich",
        "type": "attack",
        "cost": 1,
        "damage": 8,
        "color": BLUE,
        "tooltip": "Schnell. Günstig. Enttäuschend.",
        "rarity": "common",
        "effect": "damage"
    },
    {
        "name": "Schwertstreich",
        "type": "attack",
        "cost": 2,
        "damage": 14,
        "color": GREY,
        "tooltip": "Klassisch. Effektiv. Langweilig.",
        "rarity": "common",
        "effect": "damage"
    },
    {
        "name": "Nuclear Option",
        "type": "attack",
        "cost": 3,
        "damage": 45,
        "color": (255, 100, 0),
        "tooltip": "Overkill ist keine Einstellung, sondern ein Lebensgefühl.",
        "rarity": "rare",
        "effect": "nuke"
    },
    {
        "name": "Coin Flip",
        "type": "attack",
        "cost": 1,
        "damage": 0,
        "color": GOLD,
        "tooltip": "50% Chance auf 25 Schaden. 50% Chance auf Selbstschaden. Glückwunsch.",
        "rarity": "uncommon",
        "effect": "coinflip"
    },
    {
        "name": "Tax Evasion",
        "type": "attack",
        "cost": 2,
        "damage": 12,
        "color": GREY_DARK,
        "tooltip": "Schaden = dein aktuelles Gold / 10. Steueroasen sind effizient.",
        "rarity": "uncommon",
        "effect": "tax_evasion"
    },
    {
        "name": "Gambling Addiction",
        "type": "attack",
        "cost": 1,
        "damage": 0,
        "color": PURPLE,
        "tooltip": "Verliere 10 Gold. Füge 1-40 Schaden zu. EMPFOHLEN VON EXPERTEN.",
        "rarity": "uncommon",
        "effect": "gambling"
    },
    # ═══ SPECIAL ═══
    {
        "name": "Double Spin",
        "type": "special",
        "cost": 2,
        "damage": 0,
        "color": CYAN,
        "tooltip": "Drehe den Slot NOCHMAL. Chaos verdoppelt.",
        "rarity": "uncommon",
        "effect": "double_spin"
    },
    {
        "name": "Greed",
        "type": "special",
        "cost": 1,
        "damage": 0,
        "color": GOLD,
        "tooltip": "+15 Gold sofort. -5 Maximale HP. Gier ist ihr eigener Lohn.",
        "rarity": "common",
        "effect": "greed"
    },
    {
        "name": "Summon Chicken",
        "type": "special",
        "cost": 1,
        "damage": 0,
        "color": (255, 230, 100),
        "tooltip": "Ein Huhn erscheint. Es tut... irgendetwas. Wer weiß.",
        "rarity": "common",
        "effect": "chicken"
    },
    {
        "name": "Potion of Chaos",
        "type": "special",
        "cost": 0,
        "damage": 0,
        "color": (180, 50, 180),
        "tooltip": "Komplett zufällig. Könnte alles sein. Oder nichts. Kostenlos!",
        "rarity": "uncommon",
        "effect": "chaos"
    },
    # ═══ DEFENSE ═══
    {
        "name": "Schild",
        "type": "defense",
        "cost": 1,
        "damage": 0,
        "block": 8,
        "color": BLUE,
        "tooltip": "Blockt 8 Schaden. Nicht glamourös, aber ehrlich.",
        "rarity": "common",
        "effect": "block"
    },
    {
        "name": "Eisenwand",
        "type": "defense",
        "cost": 2,
        "damage": 0,
        "block": 18,
        "color": GREY,
        "tooltip": "Blockt 18 Schaden. Sehr schwer. Schlechtes Laufschuh.",
        "rarity": "uncommon",
        "effect": "block"
    },
    {
        "name": "Heilkraut",
        "type": "defense",
        "cost": 1,
        "damage": 0,
        "heal": 10,
        "color": GREEN,
        "tooltip": "Heilt 10 HP. Schmeckt schrecklich. Wirkt trotzdem.",
        "rarity": "common",
        "effect": "heal"
    },
    {
        "name": "Vampirbiss",
        "type": "attack",
        "cost": 2,
        "damage": 10,
        "heal": 5,
        "color": RED_DARK,
        "tooltip": "10 Schaden. 5 HP zurück. Nicht schlecht für einen Biss.",
        "rarity": "uncommon",
        "effect": "lifesteal"
    },
    # ═══ RARE ═══
    {
        "name": "JACKPOT KARTE",
        "type": "special",
        "cost": 3,
        "damage": 0,
        "color": GOLD,
        "tooltip": "Dreht den Slot 3x hintereinander. Kein Tipp vom Haus.",
        "rarity": "rare",
        "effect": "triple_spin"
    },
    {
        "name": "Das Ende",
        "type": "attack",
        "cost": 3,
        "damage": 0,
        "color": BLACK,
        "tooltip": "Fügt Schaden = Max HP des Feindes / 3 zu. Keine Verhandlung.",
        "rarity": "rare",
        "effect": "execrate"
    },
    # ═══ NEUE KARTEN: ANGRIFF ═══
    {
        "name": "Doppelhieb",
        "type": "attack",
        "cost": 2,
        "damage": 7,
        "color": RED,
        "tooltip": "Trifft 2x für je 7. Mathe ist hart.",
        "rarity": "common",
        "effect": "double_strike"
    },
    {
        "name": "Glückstreffer",
        "type": "attack",
        "cost": 1,
        "damage": 6,
        "color": GREEN,
        "tooltip": "6 Schaden. 30% Chance auf 3x Schaden!",
        "rarity": "uncommon",
        "effect": "lucky_hit"
    },
    {
        "name": "Wutausbruch",
        "type": "attack",
        "cost": 2,
        "damage": 0,
        "color": ORANGE,
        "tooltip": "Schaden = doppelt so viel HP wie dir fehlt. Schmerz lohnt sich.",
        "rarity": "uncommon",
        "effect": "rage"
    },
    {
        "name": "Bestechung",
        "type": "attack",
        "cost": 1,
        "damage": 0,
        "color": GOLD,
        "tooltip": "Zahle 20 Gold, um 30 Schaden zu kaufen. Korruption wirkt.",
        "rarity": "uncommon",
        "effect": "bribe"
    },
    {
        "name": "All In",
        "type": "attack",
        "cost": 3,
        "damage": 0,
        "color": RED_DARK,
        "tooltip": "Setze dein GESAMTES Gold ein. Schaden = Gold. Danach pleite.",
        "rarity": "rare",
        "effect": "all_in"
    },
    # ═══ NEUE KARTEN: DEFENSE / SUPPORT ═══
    {
        "name": "Bunker",
        "type": "defense",
        "cost": 3,
        "damage": 0,
        "block": 30,
        "color": GREY,
        "tooltip": "Blockt 30 Schaden. Sehr sicher. Sehr langweilig.",
        "rarity": "uncommon",
        "effect": "block"
    },
    {
        "name": "Zweite Luft",
        "type": "defense",
        "cost": 1,
        "damage": 0,
        "heal": 0,
        "color": GREEN,
        "tooltip": "Heilt 25% deiner fehlenden HP. Tief durchatmen.",
        "rarity": "uncommon",
        "effect": "second_wind"
    },
    {
        "name": "Reflektor",
        "type": "defense",
        "cost": 2,
        "damage": 0,
        "block": 10,
        "color": CYAN,
        "tooltip": "+10 Block. Reflektiert nächsten Schaden zurück!",
        "rarity": "rare",
        "effect": "reflect"
    },
    {
        "name": "Adrenalin",
        "type": "special",
        "cost": 0,
        "damage": 0,
        "color": CYAN,
        "tooltip": "+2 Energie sofort. Ziehe 1 Karte. Komplett legal.",
        "rarity": "uncommon",
        "effect": "adrenaline"
    },
    {
        "name": "Krafttraining",
        "type": "special",
        "cost": 1,
        "damage": 0,
        "color": ORANGE,
        "tooltip": "+2 Stärke dauerhaft. No pain, no gain.",
        "rarity": "uncommon",
        "effect": "train"
    },
    # ═══ NEUE KARTEN: CHAOS / SLOT ═══
    {
        "name": "Manipulierter Würfel",
        "type": "special",
        "cost": 1,
        "damage": 0,
        "color": PURPLE,
        "tooltip": "+2 Glücksrunden. Die Slots mögen dich jetzt.",
        "rarity": "uncommon",
        "effect": "loaded_dice"
    },
    {
        "name": "Münzregen",
        "type": "special",
        "cost": 1,
        "damage": 0,
        "color": GOLD,
        "tooltip": "+10 Gold pro gespielter Karte diese Runde. Kassieren!",
        "rarity": "uncommon",
        "effect": "coin_rain"
    },
    {
        "name": "Hühnerschwarm",
        "type": "special",
        "cost": 2,
        "damage": 0,
        "color": (255, 230, 100),
        "tooltip": "Beschwört 3 Hühner. Jedes tut etwas Zufälliges. Gott helfe uns.",
        "rarity": "rare",
        "effect": "chicken_swarm"
    },
    {
        "name": "Russisch Roulette",
        "type": "attack",
        "cost": 0,
        "damage": 0,
        "color": BLACK,
        "tooltip": "1/6 Chance: du verlierst 40 HP. Sonst: 40 Schaden. Gratis!",
        "rarity": "rare",
        "effect": "roulette"
    },
    {
        "name": "Neustart",
        "type": "special",
        "cost": 1,
        "damage": 0,
        "color": BLUE,
        "tooltip": "Wirf deine Hand ab, ziehe komplett neu. Frische Karten!",
        "rarity": "common",
        "effect": "redraw"
    },
    # ═══ NEUE KARTEN: EXTRA ═══
    {
        "name": "Pesthauch",
        "type": "attack",
        "cost": 1,
        "damage": 8,
        "color": GREEN_DARK,
        "tooltip": "8 Schaden. Gegner brennt 2 Runden. Riecht nicht gut.",
        "rarity": "uncommon",
        "effect": "plague_breath"
    },
    {
        "name": "Schildwall",
        "type": "defense",
        "cost": 1,
        "damage": 0,
        "block": 0,
        "color": BLUE,
        "tooltip": "Block = 3 × Karten in der Hand. Mehr Karten = mehr Schutz.",
        "rarity": "uncommon",
        "effect": "shield_wall"
    },
    {
        "name": "Berserker",
        "type": "attack",
        "cost": 0,
        "damage": 20,
        "color": RED_DARK,
        "tooltip": "Gratis! 20 Schaden. Kostet dauerhaft 3 Max HP. Wer braucht schon Gesundheit.",
        "rarity": "uncommon",
        "effect": "berserker"
    },
    {
        "name": "Raubzug",
        "type": "attack",
        "cost": 2,
        "damage": 12,
        "color": GOLD_DARK,
        "tooltip": "12 Schaden. Erhalte Gold = Rüstungswert des Gegners. Plündern macht Spaß.",
        "rarity": "uncommon",
        "effect": "pillage"
    },
    {
        "name": "Eisensturm",
        "type": "attack",
        "cost": 2,
        "damage": 0,
        "color": GREY,
        "tooltip": "Schaden = dein aktueller Block. Nutze deinen Schutz als Waffe!",
        "rarity": "uncommon",
        "effect": "iron_storm"
    },
    {
        "name": "Schattenschritt",
        "type": "special",
        "cost": 1,
        "damage": 0,
        "color": PURPLE,
        "tooltip": "+1 Energie. Nächste Karte kostet 0. Husch.",
        "rarity": "rare",
        "effect": "shadow_step"
    },
    {
        "name": "Vergeltung",
        "type": "attack",
        "cost": 1,
        "damage": 0,
        "color": ORANGE,
        "tooltip": "Schaden = Schaden den du bisher diesen Run genommen hast / 10. Hass zahlt sich aus.",
        "rarity": "rare",
        "effect": "retribution"
    },
    # ═══ EXHAUST-KARTEN (einmalig, dann verbraucht) ═══
    {
        "name": "Vernichtung",
        "type": "attack",
        "cost": 2,
        "damage": 60,
        "color": (255, 60, 30),
        "tooltip": "60 Schaden! VERBRAUCHT sich nach Gebrauch (weg aus dem Deck).",
        "rarity": "rare",
        "effect": "annihilate",
        "exhaust": True
    },
    {
        "name": "Letzter Trumpf",
        "type": "special",
        "cost": 2,
        "damage": 0,
        "color": GOLD,
        "tooltip": "Heile auf Maximum + 3 Stärke. VERBRAUCHT sich danach.",
        "rarity": "rare",
        "effect": "last_resort",
        "exhaust": True
    },
    {
        "name": "Goldrausch",
        "type": "special",
        "cost": 0,
        "damage": 0,
        "color": GOLD,
        "tooltip": "+60 Gold sofort. VERBRAUCHT sich danach. Schnelles Geld.",
        "rarity": "uncommon",
        "effect": "gold_rush",
        "exhaust": True
    },
    # ═══ NEUE KARTEN v1.8.0: Gift-, Debuff- & Risiko-Archetypen ═══
    {
        "name": "Giftklinge",
        "type": "attack",
        "cost": 1,
        "damage": 6,
        "color": GREEN_DARK,
        "tooltip": "6 Schaden + 3 Gift. Gift tickt JEDE Runde und sinkt nicht. Geduld zahlt sich aus.",
        "rarity": "common",
        "effect": "poison_blade"
    },
    {
        "name": "Toxische Wolke",
        "type": "special",
        "cost": 2,
        "damage": 0,
        "color": GREEN_DARK,
        "tooltip": "5 Gift auf den Gegner. Kein Schaden jetzt – dafür ein langsamer, hässlicher Tod.",
        "rarity": "uncommon",
        "effect": "toxic_cloud"
    },
    {
        "name": "Säurefass",
        "type": "attack",
        "cost": 2,
        "damage": 8,
        "color": GREEN_DARK,
        "tooltip": "8 Schaden, dann VERDOPPELT sich das Gift auf dem Gegner. Chemie ist toll.",
        "rarity": "rare",
        "effect": "acid_barrel"
    },
    {
        "name": "Schwachstelle",
        "type": "attack",
        "cost": 1,
        "damage": 8,
        "color": ORANGE,
        "tooltip": "8 Schaden + 2 Runden Verwundbar (Gegner nimmt +50% Schaden).",
        "rarity": "uncommon",
        "effect": "expose"
    },
    {
        "name": "Henkersbeil",
        "type": "attack",
        "cost": 2,
        "damage": 12,
        "color": RED_DARK,
        "tooltip": "12 Schaden. +50% gegen vergiftete Gegner. Das Beil kennt keine Gnade.",
        "rarity": "rare",
        "effect": "executioner"
    },
    {
        "name": "Regenerationstrank",
        "type": "special",
        "cost": 1,
        "damage": 0,
        "heal": 0,
        "color": GREEN,
        "tooltip": "+4 Regeneration: heilt 4, dann 3, dann 2 ... HP pro Rundenstart.",
        "rarity": "common",
        "effect": "regen_potion"
    },
    {
        "name": "Stachelhaut",
        "type": "defense",
        "cost": 1,
        "damage": 0,
        "block": 8,
        "color": ORANGE,
        "tooltip": "+8 Block und +4 Dornen (reflektiert Schaden bei jedem Gegnertreffer, ganzer Kampf).",
        "rarity": "uncommon",
        "effect": "spike_skin"
    },
    {
        "name": "Blutpakt",
        "type": "special",
        "cost": 0,
        "damage": 0,
        "color": RED_DARK,
        "tooltip": "Zahle 5 HP, erhalte +2 Energie. Der Pakt fragt nicht zweimal.",
        "rarity": "rare",
        "effect": "blood_pact"
    },
    # ═══ NEUE KARTEN v1.9.0: Klassen-Archetypen (Ritter / Hochstapler / Hexe) ═══
    {
        "name": "Kriegsschrei",
        "type": "special",
        "cost": 1,
        "damage": 0,
        "color": ORANGE,
        "tooltip": "+2 Stärke und +6 Block. Brüll, bis es weh tut.",
        "rarity": "common",
        "effect": "warcry"
    },
    {
        "name": "Schildbuckel",
        "type": "attack",
        "cost": 1,
        "damage": 0,
        "color": BLUE,
        "tooltip": "Schaden = dein aktueller Block. Block bleibt erhalten.",
        "rarity": "uncommon",
        "effect": "shield_bash"
    },
    {
        "name": "Aderlass",
        "type": "attack",
        "cost": 1,
        "damage": 4,
        "color": RED_DARK,
        "tooltip": "4 Schaden + 2 Gift, heile 3 HP. Geben und Nehmen.",
        "rarity": "common",
        "effect": "bloodletting"
    },
    {
        "name": "Glückssträhne",
        "type": "special",
        "cost": 1,
        "damage": 0,
        "color": GOLD,
        "tooltip": "+2 Glücksrunden und ziehe 1 Karte. Es läuft!",
        "rarity": "common",
        "effect": "lucky_streak"
    },
    {
        "name": "Giftmischung",
        "type": "special",
        "cost": 1,
        "damage": 0,
        "color": GREEN_DARK,
        "tooltip": "+7 Gift auf den Gegner. Gebraut mit Liebe und Hass.",
        "rarity": "uncommon",
        "effect": "brew_poison"
    },
    {
        "name": "Kartentrick",
        "type": "special",
        "cost": 1,
        "damage": 0,
        "color": CYAN,
        "tooltip": "Ziehe 2 Karten. Nichts in den Ärmeln. Versprochen.",
        "rarity": "uncommon",
        "effect": "card_trick"
    },
    # ═══ NEUE KARTEN v1.10.0: Grosses Content-Update ═══
    {
        "name": "Klingensturm", "type": "attack", "cost": 2, "damage": 6, "color": RED,
        "tooltip": "Triff 3× für je 6 (+Stärke). Wirbelwind aus Stahl.",
        "rarity": "uncommon", "effect": "blade_flurry"
    },
    {
        "name": "Hinrichtung", "type": "attack", "cost": 2, "damage": 14, "color": RED_DARK,
        "tooltip": "14 Schaden. DOPPELT, wenn der Gegner unter 40% HP ist.",
        "rarity": "rare", "effect": "execute_low"
    },
    {
        "name": "Giftdartwurf", "type": "attack", "cost": 0, "damage": 3, "color": GREEN_DARK,
        "tooltip": "3 Schaden + 2 Gift. Verbraucht sich. Schnell und fies.",
        "rarity": "common", "effect": "poison_dart", "exhaust": True
    },
    {
        "name": "Giftausbruch", "type": "attack", "cost": 1, "damage": 0, "color": GREEN,
        "tooltip": "Schaden = Gift des Gegners. Danach halbiert sich sein Gift.",
        "rarity": "uncommon", "effect": "venom_burst"
    },
    {
        "name": "Rückhand", "type": "attack", "cost": 1, "damage": 9, "color": ORANGE,
        "tooltip": "9 Schaden und ziehe 1 Karte. Lässig nebenbei.",
        "rarity": "common", "effect": "backhand"
    },
    {
        "name": "Bollwerk", "type": "defense", "cost": 2, "block": 18, "color": BLUE,
        "tooltip": "+18 Block. Eine Wand aus Eisen.",
        "rarity": "uncommon", "effect": "block"
    },
    {
        "name": "Konterstoß", "type": "defense", "cost": 1, "block": 6, "color": CYAN,
        "tooltip": "+6 Block und reflektiere den nächsten Angriff.",
        "rarity": "uncommon", "effect": "counter"
    },
    {
        "name": "Ausweichrolle", "type": "defense", "cost": 1, "damage": 0, "color": CYAN,
        "tooltip": "Weiche dem nächsten Gegnerangriff komplett aus.",
        "rarity": "uncommon", "effect": "evade"
    },
    {
        "name": "Energieschub", "type": "special", "cost": 0, "damage": 0, "color": GOLD,
        "tooltip": "+2 Energie sofort. Verbraucht sich.",
        "rarity": "uncommon", "effect": "energize", "exhaust": True
    },
    {
        "name": "Tiefes Ziehen", "type": "special", "cost": 1, "damage": 0, "color": CYAN,
        "tooltip": "Ziehe 3 Karten. Verbraucht sich. Hol dir Optionen.",
        "rarity": "uncommon", "effect": "deep_draw", "exhaust": True
    },
    {
        "name": "Berserkerwut", "type": "special", "cost": 0, "damage": 0, "color": RED_DARK,
        "tooltip": "+3 Stärke, aber −4 HP. Schmerz ist nur Schwäche, die geht.",
        "rarity": "uncommon", "effect": "berserk_rage"
    },
    {
        "name": "Meditation", "type": "special", "cost": 1, "damage": 0, "color": GREEN,
        "tooltip": "+2 Stärke und +3 Regeneration. Innere Ruhe, äußere Gewalt.",
        "rarity": "rare", "effect": "meditate"
    },
    {
        "name": "Goldader", "type": "attack", "cost": 1, "damage": 0, "color": GOLD,
        "tooltip": "+20 Gold, dann Schaden = Gold / 12. Reichtum tut weh.",
        "rarity": "uncommon", "effect": "midas"
    },
    {
        "name": "Rüstungsbruch", "type": "attack", "cost": 1, "damage": 7, "color": GREY,
        "tooltip": "7 Schaden und −3 Rüstung des Gegners (für den Kampf).",
        "rarity": "uncommon", "effect": "sunder"
    },
    # ═══ NEUE KARTEN v1.12.0: Frost, Betäubung, Verhängnis, Wut, Fokus ═══
    {"name": "Frostklinge", "type": "attack", "cost": 1, "damage": 6, "color": CYAN,
     "tooltip": "6 Schaden + 2 Frost (Gegner schlägt 2 Runden schwächer).",
     "rarity": "common", "effect": "frost_strike"},
    {"name": "Betäubungshieb", "type": "attack", "cost": 2, "damage": 8, "color": BLUE,
     "tooltip": "8 Schaden + BETÄUBT: der Gegner überspringt seinen nächsten Zug.",
     "rarity": "rare", "effect": "stun_bash"},
    {"name": "Brandmal", "type": "attack", "cost": 1, "damage": 5, "color": ORANGE,
     "tooltip": "5 Schaden + Markiert: jeder Treffer macht +4 Schaden.",
     "rarity": "uncommon", "effect": "mark_strike"},
    {"name": "Verhängnis", "type": "special", "cost": 2, "damage": 0, "color": PURPLE_DARK,
     "tooltip": "Verfluche den Gegner: in 3 Runden trifft ihn ein massiver Schlag.",
     "rarity": "rare", "effect": "doom_card"},
    {"name": "Klingenwalzer", "type": "attack", "cost": 2, "damage": 4, "color": RED,
     "tooltip": "Triff 5× für je 4 (+Stärke). Tanz mit der Klinge.",
     "rarity": "uncommon", "effect": "flurry5"},
    {"name": "Hinterhalt", "type": "attack", "cost": 1, "damage": 7, "color": PURPLE_DARK,
     "tooltip": "7 Schaden. DOPPELT gegen betäubte oder gefrorene Gegner.",
     "rarity": "uncommon", "effect": "ambush"},
    {"name": "Seelenschnitt", "type": "attack", "cost": 2, "damage": 0, "color": CURSE_COL,
     "tooltip": "10 Schaden, +3 pro Debuff auf dem Gegner. Belohnt Status-Spiel.",
     "rarity": "rare", "effect": "soul_cut"},
    {"name": "Blutrausch", "type": "attack", "cost": 1, "damage": 7, "color": RED_DARK,
     "tooltip": "7 Schaden und +1 Wut (Stärke wächst jede Runde).",
     "rarity": "uncommon", "effect": "bloodrage"},
    {"name": "Urteil", "type": "attack", "cost": 3, "damage": 0, "color": GOLD,
     "tooltip": "12 Schaden – aber 30, wenn der Gegner unter Verhängnis steht.",
     "rarity": "rare", "effect": "judgement"},
    {"name": "Eisregen", "type": "attack", "cost": 2, "damage": 8, "color": CYAN,
     "tooltip": "8 Schaden + 2 Frost. Kalt serviert.",
     "rarity": "common", "effect": "icestorm"},
    {"name": "Eingraben", "type": "defense", "cost": 1, "damage": 0, "color": BLUE,
     "tooltip": "Verdopple deinen aktuellen Block. Stell dich fest hin.",
     "rarity": "uncommon", "effect": "entrench"},
    {"name": "Frostpanzer", "type": "defense", "cost": 1, "block": 8, "color": CYAN,
     "tooltip": "+8 Block und +2 Frost auf den Gegner.",
     "rarity": "uncommon", "effect": "frost_armor"},
    {"name": "Ausdauer", "type": "defense", "cost": 1, "block": 6, "color": GREEN,
     "tooltip": "+6 Block und heile 4 HP. Durchatmen.",
     "rarity": "common", "effect": "endure"},
    {"name": "Festungswall", "type": "defense", "cost": 2, "block": 20, "color": BLUE,
     "tooltip": "+20 Block. Wie eine Mauer.",
     "rarity": "uncommon", "effect": "block"},
    {"name": "Kampfrausch", "type": "special", "cost": 1, "damage": 0, "color": RED_DARK,
     "tooltip": "+2 Wut: deine Stärke wächst jede Runde. Verbraucht sich.",
     "rarity": "rare", "effect": "rage_power", "exhaust": True},
    {"name": "Konzentration", "type": "special", "cost": 0, "damage": 0, "color": ORANGE,
     "tooltip": "+6 Fokus: deine nächste Angriffskarte macht +6 Schaden.",
     "rarity": "common", "effect": "focus_power"},
    {"name": "Sturmlauf", "type": "special", "cost": 0, "damage": 0, "color": GOLD,
     "tooltip": "+2 Energie und ziehe 1 Karte. Verbraucht sich.",
     "rarity": "uncommon", "effect": "rush", "exhaust": True},
    {"name": "Opfergabe", "type": "special", "cost": 0, "damage": 0, "color": RED_DARK,
     "tooltip": "−6 HP, dafür +2 Stärke und +1 Energie. Blut für Macht.",
     "rarity": "uncommon", "effect": "sacrifice_card"},
    {"name": "Giftschwade", "type": "special", "cost": 2, "damage": 0, "color": GREEN_DARK,
     "tooltip": "+9 Gift auf den Gegner. Ein dicker Nebel des Todes.",
     "rarity": "uncommon", "effect": "mega_poison"},
    {"name": "Reinigung", "type": "special", "cost": 1, "damage": 0, "color": WHITE,
     "tooltip": "+6 Block, entfernt Brennen/Gift/Verwundbar von dir.",
     "rarity": "uncommon", "effect": "cleanse"},
    {"name": "Wildes Glück", "type": "special", "cost": 1, "damage": 0, "color": GOLD,
     "tooltip": "50%: +3 Stärke. Sonst: +6 Gift auf den Gegner. Win-win-ish.",
     "rarity": "common", "effect": "wild_luck"},
    {"name": "Henkersmahlzeit", "type": "attack", "cost": 2, "damage": 14, "color": RED_DARK,
     "tooltip": "14 Schaden und heile um den verursachten Schaden. Festmahl.",
     "rarity": "rare", "effect": "feast"},
]

# ═══════════════════════════════════════════════
# FLUCH-KARTEN (kommen NUR durch Events ins Deck)
# ═══════════════════════════════════════════════
CURSE_DEFINITIONS = [
    {
        "name": "Fluch: Übelkeit",
        "type": "curse",
        "cost": 0,
        "damage": 0,
        "color": CURSE_COL,
        "tooltip": "FLUCH. Beim Spielen: -6 HP. Verbrenne sie im Shop.",
        "rarity": "curse",
        "effect": "curse_nausea"
    },
    {
        "name": "Fluch: Pech",
        "type": "curse",
        "cost": 0,
        "damage": 0,
        "color": CURSE_COL,
        "tooltip": "FLUCH. Beim Spielen: -10 Gold. Nutzlos und teuer.",
        "rarity": "curse",
        "effect": "curse_unluck"
    },
    {
        "name": "Fluch: Last",
        "type": "curse",
        "cost": 0,
        "damage": 0,
        "color": CURSE_COL,
        "tooltip": "FLUCH. Beim Spielen: -1 Energie diese Runde. Schwer wie Blei.",
        "rarity": "curse",
        "effect": "curse_burden"
    },
]

# ═══════════════════════════════════════════════
# RELIKTE (permanente passive Boni für den Run)
# ═══════════════════════════════════════════════
RELIC_DEFINITIONS = [
    {"id": "gold_boost",     "name": "Goldener Finger", "emoji": "🪙",
     "desc": "+30% Gold von besiegten Gegnern.", "rarity": "common"},
    {"id": "start_block",    "name": "Eiserner Wille",  "emoji": "🛡️",
     "desc": "Beginne jeden Kampf mit 12 Block.", "rarity": "common"},
    {"id": "bonus_spin",     "name": "Glücksbringer",   "emoji": "🎰",
     "desc": "+1 Slot-Dreh pro Runde.", "rarity": "rare"},
    {"id": "combat_strength","name": "Kriegsbanner",    "emoji": "🪖",
     "desc": "+3 Stärke – einmalig beim Aufheben.", "rarity": "uncommon"},
    {"id": "heal_on_kill",   "name": "Herzstein",       "emoji": "❤️",
     "desc": "Heile 8 HP wenn ein Gegner stirbt.", "rarity": "common"},
    {"id": "bonus_energy",   "name": "Energiekern",     "emoji": "⚡",
     "desc": "+1 Max Energie (sofort & dauerhaft).", "rarity": "rare"},
    {"id": "always_lucky",   "name": "Gezinkte Würfel", "emoji": "🎲",
     "desc": "Jeder Slot-Dreh ist glücklich.", "rarity": "rare"},
    {"id": "interest",       "name": "Spardose",        "emoji": "💰",
     "desc": "Kampfbeginn: +1 Gold je 25 Gold (max 10).", "rarity": "uncommon"},
    {"id": "thorns",         "name": "Dornenpanzer",    "emoji": "🌵",
     "desc": "Reflektiere 5 Schaden bei jedem Gegnerangriff.", "rarity": "uncommon"},
    {"id": "first_free",     "name": "Falsches Ass",    "emoji": "🎴",
     "desc": "Erste Karte jeder Runde kostet 0 Energie.", "rarity": "rare"},
    {"id": "max_hp_relic",   "name": "Lebensring",      "emoji": "💍",
     "desc": "+20 Max HP (sofort & dauerhaft).", "rarity": "common"},
    {"id": "chicken_relic",  "name": "Hühner-Totem",    "emoji": "🐔",
     "desc": "Kampfbeginn: 40% Chance ein Huhn zu beschwören.", "rarity": "uncommon"},
    # ─── Neue Relikte (v1.8.0) ───
    {"id": "poison_boost",   "name": "Giftring",        "emoji": "🐍",
     "desc": "Alle deine Gift-Effekte geben +1 Gift extra.", "rarity": "uncommon"},
    {"id": "gamble_discount","name": "Würfelbecher",    "emoji": "🥤",
     "desc": "Glücksrad-Einsatz steigt nicht mehr (bleibt bei 25 Gold).", "rarity": "uncommon"},
    {"id": "trophy",         "name": "Trophäensammlung","emoji": "🏆",
     "desc": "+1 Stärke dauerhaft für jeden besiegten Boss.", "rarity": "rare"},
    {"id": "vamp_tooth",     "name": "Vampirzahn",      "emoji": "🦷",
     "desc": "Drilling im Slot heilt dich um 10 HP.", "rarity": "uncommon"},
    {"id": "anatomy",        "name": "Anatomiebuch",    "emoji": "📕",
     "desc": "Verwundbar, das du verursachst, hält +1 Runde länger.", "rarity": "common"},
    {"id": "fortune_cookie", "name": "Glückskeks",      "emoji": "🥠",
     "desc": "Kampfbeginn: +1 Glücksrunde für den Slot.", "rarity": "common"},
    # ─── Neue Relikte (v1.9.0, Klassen-Synergien) ───
    {"id": "witch_cauldron", "name": "Hexenkessel",     "emoji": "🧪",
     "desc": "Kampfbeginn: der Gegner startet mit 3 Gift.", "rarity": "uncommon"},
    {"id": "watchtower",     "name": "Wachturm",        "emoji": "🗼",
     "desc": "Zu Beginn JEDER Runde: +6 Block.", "rarity": "rare"},
    {"id": "four_leaf",      "name": "Vierblättriger Klee", "emoji": "🍀",
     "desc": "Kampfbeginn: +1 Slot-Dreh UND +1 Glücksrunde.", "rarity": "rare"},
    # ─── Neue Relikte (v1.10.0) ───
    {"id": "antidote",       "name": "Gegengift",       "emoji": "🧪",
     "desc": "Du bist immun gegen Gift (kein Gift-Schaden an dir).", "rarity": "uncommon"},
    {"id": "purse",          "name": "Dukatenbeutel",   "emoji": "👛",
     "desc": "Kampfbeginn: +8 Gold.", "rarity": "common"},
    {"id": "leech_charm",    "name": "Aderlass-Amulett", "emoji": "🩸",
     "desc": "Heile 2 HP, wenn du eine Angriffskarte spielst.", "rarity": "uncommon"},
    {"id": "mirror_shield",  "name": "Spiegelschild",   "emoji": "🪞",
     "desc": "Kampfbeginn: Reflektor aktiv (wirft 1. Angriff zurück).", "rarity": "uncommon"},
    {"id": "phoenix",        "name": "Phönixfeder",     "emoji": "🪶",
     "desc": "Einmal pro Run überlebst du den Tod mit 1 HP.", "rarity": "rare"},
    {"id": "tip_jar",        "name": "Trinkglas",       "emoji": "🫙",
     "desc": "+2 Gold bei jedem Slot-Dreh.", "rarity": "common"},
    {"id": "extra_draw",     "name": "Doppeldecker",    "emoji": "🃏",
     "desc": "Ziehe +1 Karte zu Beginn jeder Runde.", "rarity": "rare"},
    {"id": "counterfeit",    "name": "Falschgeld",      "emoji": "💸",
     "desc": "Shop & Glücksrad kosten 25% weniger.", "rarity": "uncommon"},
    {"id": "chainmail",      "name": "Kettenhemd",      "emoji": "⛓️",
     "desc": "Jeder erlittene Treffer macht 2 weniger Schaden.", "rarity": "uncommon"},
    # ─── Neue Relikte (v1.12.0, Status-Synergien) ───
    {"id": "frostbite",      "name": "Eiszapfen-Amulett", "emoji": "❄️",
     "desc": "Kampfbeginn: der Gegner startet mit 2 Frost.", "rarity": "uncommon"},
    {"id": "branding",       "name": "Brandeisen",      "emoji": "🔥",
     "desc": "Kampfbeginn: der Gegner ist mit +3 markiert.", "rarity": "uncommon"},
    {"id": "rage_totem",     "name": "Wuttotem",        "emoji": "😤",
     "desc": "Kampfbeginn: +1 Wut (Stärke wächst jede Runde).", "rarity": "rare"},
    {"id": "focus_lens",     "name": "Fokuslinse",      "emoji": "🔎",
     "desc": "+2 Fokus zu Beginn jeder Runde.", "rarity": "uncommon"},
    {"id": "time_glass",     "name": "Zeitsanduhr",     "emoji": "⏳",
     "desc": "+1 Energie in der ersten Runde jedes Kampfes.", "rarity": "rare"},
    {"id": "card_master",    "name": "Kartenmeister",   "emoji": "🎴",
     "desc": "+2 Karten in der ersten Runde jedes Kampfes.", "rarity": "rare"},
    {"id": "lucky_coin",     "name": "Glücksmünze",     "emoji": "🪙",
     "desc": "+1 Gold für jede gespielte Karte.", "rarity": "common"},
    {"id": "thorn_crown",    "name": "Dornenkrone",     "emoji": "👑",
     "desc": "Kampfbeginn: +4 Dornen (reflektiert Schaden).", "rarity": "uncommon"},
    {"id": "scavenger",      "name": "Aasfresser",      "emoji": "🦅",
     "desc": "Heile 10% deiner Max-HP, wenn ein Gegner stirbt.", "rarity": "uncommon"},
    {"id": "berserker_blood","name": "Berserkerblut",   "emoji": "🩸",
     "desc": "Startest du einen Kampf unter 50% HP: +3 Stärke.", "rarity": "uncommon"},
    {"id": "doom_bell",      "name": "Schicksalsglocke", "emoji": "🔔",
     "desc": "35% Chance, dass der Gegner zu Kampfbeginn Verhängnis bekommt.", "rarity": "rare"},
    {"id": "ice_heart",      "name": "Eisherz",         "emoji": "🧊",
     "desc": "Du weichst dem ersten Gegnertreffer jedes Kampfes aus.", "rarity": "rare"},
]

# ═══════════════════════════════════════════════
# START-KLASSEN  (wählbar vor dem Run)
# deck = Liste von Kartennamen (Startdeck), relic = Start-Relikt-ID
# ═══════════════════════════════════════════════
CLASS_DEFINITIONS = [
    {
        "id": "knight",
        "name": "Der Ritter",
        "emoji": "🛡️",
        "color": BLUE,
        "desc": "Block & Stärke. Hält viel aus, schlägt stetig zu.",
        "perk": "Start mit Relikt 'Eiserner Wille' (+12 Block/Kampf).",
        "relic": "start_block",
        "deck": ["Schneller Stich", "Schneller Stich", "Schneller Stich",
                 "Schwertstreich", "Schwertstreich",
                 "Schild", "Schild", "Schild",
                 "Kriegsschrei", "Schildbuckel"],
    },
    {
        "id": "gambler",
        "name": "Der Hochstapler",
        "emoji": "🎰",
        "color": GOLD,
        "desc": "Slots & Glück. Lebt vom Risiko und den großen Drehern.",
        "perk": "Start mit Relikt 'Glücksbringer' (+1 Slot-Dreh/Runde).",
        "relic": "bonus_spin",
        "deck": ["Schneller Stich", "Schneller Stich", "Schneller Stich",
                 "Schild", "Schild",
                 "Coin Flip", "Coin Flip", "Greed",
                 "Glückssträhne", "Double Spin"],
    },
    {
        "id": "witch",
        "name": "Die Hexe",
        "emoji": "🧪",
        "color": GREEN,
        "desc": "Gift & Verfall. Lässt Gegner langsam dahinsiechen.",
        "perk": "Start mit Relikt 'Giftring' (+1 auf alle Gift-Effekte).",
        "relic": "poison_boost",
        "deck": ["Schneller Stich", "Schneller Stich",
                 "Schild", "Schild",
                 "Giftklinge", "Giftklinge", "Giftklinge",
                 "Aderlass", "Heilkraut", "Toxische Wolke"],
    },
]

# ═══════════════════════════════════════════════
# ZUFALLS-EVENTS (zwischen den Etagen)
# ═══════════════════════════════════════════════
EVENT_DEFINITIONS = [
    {
        "title": "Das Untergrund-Casino",
        "asset": "casino",
        "emoji": "🎲",
        "text": "Eine Falltür, rauchige Luft, große Einsätze. Hier verliert man "
                "mehr als nur Gold – oder gewinnt alles.",
        "options": [
            {"label": "Alles auf Rot", "desc": "50%: Gold VERDOPPELN. 50%: ALLES Gold weg.",
             "effect": "casino_double_or_nothing"},
            {"label": "Blutpoker", "desc": "Setze 20 HP: 60% gewinnst du ein Relikt, 40% nur Schmerz.",
             "effect": "casino_blood_poker"},
            {"label": "Mystery-Box", "desc": "30 Gold: Karte, Relikt, Heilung – oder ein Fluch.",
             "effect": "casino_mystery_box", "value": 30},
            {"label": "Nüchtern bleiben", "desc": "+10 Gold fürs Türsteher-Spielen", "effect": "gold", "value": 10},
        ],
    },
    {
        "title": "Der Glücksbrunnen",
        "asset": "brunnen",
        "emoji": "⛲",
        "text": "Ein alter Brunnen glitzert. Münzen liegen am verschlammten Grund.",
        "options": [
            {"label": "Münzen klauen", "desc": "+30 Gold", "effect": "gold", "value": 30},
            {"label": "Münze opfern",  "desc": "Wirf 20 Gold rein für ein Relikt", "effect": "relic_for_gold", "value": 20},
            {"label": "Weitergehen",   "desc": "Lass den Brunnen in Ruhe", "effect": "nothing"},
        ],
    },
    {
        "title": "Zwielichtiger Händler",
        "asset": "haendler",
        "emoji": "🧙",
        "text": "Eine vermummte Gestalt bietet dir 'ein ganz besonderes Geschäft' an.",
        "options": [
            {"label": "Handel annehmen", "desc": "-15 HP, dafür ein Relikt", "effect": "relic_for_hp", "value": 15},
            {"label": "Drohen",          "desc": "50%: +40 Gold. 50%: ein Fluch!", "effect": "threaten"},
            {"label": "Ablehnen",        "desc": "+10 Gold (er will dich loswerden)", "effect": "gold", "value": 10},
        ],
    },
    {
        "title": "Verlassener Schrein",
        "asset": "schrein",
        "emoji": "⛩️",
        "text": "Ein staubiger Schrein. Etwas Heiliges (oder Verfluchtes) liegt in der Luft.",
        "options": [
            {"label": "Beten",     "desc": "Heile 25 HP", "effect": "heal", "value": 25},
            {"label": "Opfern",    "desc": "-10 HP, +2 Stärke dauerhaft", "effect": "sacrifice"},
            {"label": "Plündern",  "desc": "+35 Gold, aber ein Fluch", "effect": "loot_cursed", "value": 35},
        ],
    },
    {
        "title": "Das Hühnerorakel",
        "asset": "orakel",
        "emoji": "🐔",
        "text": "Ein riesiges Huhn starrt dich weise an. Es gackert prophetisch.",
        "options": [
            {"label": "Zuhören",   "desc": "+2 Glücksrunden", "effect": "spins", "value": 2},
            {"label": "Füttern",   "desc": "-15 Gold, +15 Max HP", "effect": "feed_chicken", "value": 15},
            {"label": "Verbeugen", "desc": "Beschwöre ein Huhn (Zufall)", "effect": "chicken"},
        ],
    },
    {
        "title": "Defekter Geldautomat",
        "asset": "atm",
        "emoji": "🏧",
        "text": "Ein Geldautomat blinkt fehlerhaft. Du könntest ihn manipulieren...",
        "options": [
            {"label": "Hacken",    "desc": "50%: +50 Gold. 50%: -15 HP (Stromschlag)", "effect": "hack_atm"},
            {"label": "Einzahlen", "desc": "Verdopple bis zu 30 deines Goldes", "effect": "deposit"},
            {"label": "Treten",    "desc": "+5 Gold fällt raus", "effect": "gold", "value": 5},
        ],
    },
    {
        "title": "Trainingsraum",
        "asset": "training",
        "emoji": "🏋️",
        "text": "Ein staubiges Fitnessstudio. Die Gewichte rufen deinen Namen.",
        "options": [
            {"label": "Trainieren",  "desc": "+3 Stärke dauerhaft", "effect": "strength", "value": 3},
            {"label": "Energie tanken","desc": "+1 Max Energie", "effect": "energy"},
            {"label": "Ausruhen",    "desc": "Heile 20 HP", "effect": "heal", "value": 20},
        ],
    },
    {
        "title": "Mysteriöse Truhe",
        "asset": "truhe",
        "emoji": "🧰",
        "text": "Eine verschlossene Truhe. Etwas klappert darin. Risiko?",
        "options": [
            {"label": "Öffnen",     "desc": "Garantiert ein Relikt", "effect": "relic"},
            {"label": "Aufbrechen", "desc": "-8 HP, dafür +40 Gold", "effect": "break_chest", "value": 40},
            {"label": "Stehenlassen","desc": "Sicherheit über alles", "effect": "nothing"},
        ],
    },
]
