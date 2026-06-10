"""
Karten-/Pfad-Generierung (Slay-the-Spire-Stil).
Reine Datenstruktur ohne pygame – leicht testbar und serialisierbar.

Ein 'Akt' ist eine Karte mit ROWS Reihen; die oberste Reihe ist der Boss.
Der Spieler startet unter Reihe 0 und wählt sich Knoten für Knoten nach oben.
Nach dem Boss wird der nächste (härtere) Akt generiert -> endlos.
"""

import random

ROWS = 7          # Reihe 0 (unten) .. ROWS-1 (oben = Boss)
COLS = 6
PATHS = 6         # Anzahl Trampelpfade -> garantiert zusammenhängend

# Layout (muss mit der UI/Klickerkennung übereinstimmen)
X_LEFT = 180
X_RIGHT = 1020
Y_BOTTOM = 700
Y_TOP = 150
NODE_R = 24

NODE_TYPES = ("combat", "elite", "event", "shop", "rest", "treasure", "boss")


def _weighted_type(rng):
    r = rng.random()
    if r < 0.42:
        return "combat"
    if r < 0.58:
        return "event"
    if r < 0.68:
        return "elite"
    if r < 0.82:        # mehr Shops -> fairer
        return "shop"
    if r < 0.93:        # etwas mehr Rast
        return "rest"
    return "treasure"


def _layout(node):
    col_gap = (X_RIGHT - X_LEFT) / max(1, COLS - 1)
    row_gap = (Y_BOTTOM - Y_TOP) / max(1, ROWS - 1)
    jx = random.Random(node["row"] * 97 + node["col"] * 13).uniform(-16, 16)
    node["x"] = int(X_LEFT + node["col"] * col_gap + jx)
    node["y"] = int(Y_BOTTOM - node["row"] * row_gap)


def generate(act, seed=None):
    """Erzeugt eine Akt-Karte. Gibt ein serialisierbares Dict zurück."""
    rng = random.Random(seed) if seed is not None else random
    nodes = {}     # (row,col) -> node
    edges = set()  # ((r,c),(r2,c2))
    boss_col = COLS // 2

    def ensure(r, c):
        key = (r, c)
        if key not in nodes:
            nodes[key] = {"row": r, "col": c, "type": None, "done": False, "next": []}
        return key

    for _ in range(PATHS):
        c = rng.randint(0, COLS - 1)
        ensure(0, c)
        for r in range(ROWS - 1):
            if r == ROWS - 2:
                nc = boss_col          # alle Pfade laufen im Boss zusammen
            else:
                nc = min(COLS - 1, max(0, c + rng.choice([-1, 0, 1])))
            ensure(r, c)
            ensure(r + 1, nc)
            edges.add(((r, c), (r + 1, nc)))
            c = nc

    ensure(ROWS - 1, boss_col)

    # Kanten in die Knoten eintragen
    for a, b in edges:
        if [b[0], b[1]] not in nodes[a]["next"]:
            nodes[a]["next"].append([b[0], b[1]])

    # Typen zuweisen
    for (r, c), node in nodes.items():
        if r == 0:
            node["type"] = "combat"
        elif r == ROWS - 1:
            node["type"] = "boss"
        elif r == ROWS - 2:
            node["type"] = "rest"        # Rast direkt vor dem Boss
        else:
            t = _weighted_type(rng)
            if t == "elite" and r < 2:
                t = "combat"
            node["type"] = t
        _layout(node)

    # Mindestens 1 Shop pro Akt garantieren (sonst zu schwer)
    middle = [n for n in nodes.values() if 1 <= n["row"] <= ROWS - 3]
    if middle and not any(n["type"] == "shop" for n in middle):
        rng.choice(middle)["type"] = "shop"

    ordered = [nodes[k] for k in sorted(nodes)]
    return {"rows": ROWS, "cols": COLS, "act": act, "nodes": ordered}


# ─── Helfer zum Arbeiten mit der Karte ───

def node_map(gamemap):
    """Dict (row,col) -> node"""
    return {(n["row"], n["col"]): n for n in gamemap["nodes"]}


def row0_nodes(gamemap):
    return [n for n in gamemap["nodes"] if n["row"] == 0]


def next_nodes(gamemap, node):
    nm = node_map(gamemap)
    return [nm[(r, c)] for r, c in node["next"] if (r, c) in nm]
