"""Konstanten und Konfiguration für das gesamte Spiel"""

# Version (Save-Stände werden gegen diese Version geprüft)
GAME_VERSION = "1.8.4"

# Speicherstand-Datei (laufender Run)
SAVE_FILE = "savegame.json"

# Kompakte In-Game-Changelist (neueste oben, EINE kurze Zeile pro Version)
CHANGELOG = [
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
     "desc": "+2 Stärke zu jedem Kampfbeginn.", "rarity": "uncommon"},
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
