"""
In-Game-Updater über GitHub Releases (kostenlos, kein eigener Server).

Ablauf:
- Beim Start wird im Hintergrund die neueste Release-Version vom Repo geprüft.
- Ist eine neuere da, zeigt das Menü einen "Update"-Button.
- Klick lädt die neue .exe und tauscht die laufende gegen die neue aus
  (laufende EXE -> .old umbenennen, neue an ihre Stelle, neu starten).

Nur in der gebündelten EXE aktiv. Im Quellcode-Modus (python main.py) wird
nichts ersetzt. Fehler (kein Netz o.ä.) sind still -> dann kein Update-Button.
"""

import os
import sys
import json
import threading
import subprocess
import urllib.request

REPO = "bennetinname/slotsandswords"
API_LATEST = f"https://api.github.com/repos/{REPO}/releases/latest"
_HEADERS = {"User-Agent": "SlotsAndSwords-Updater", "Accept": "application/vnd.github+json"}

# Ergebnis des Versions-Checks
status = {"checked": False, "available": False, "version": None, "url": None}
# Fortschritt während des Downloads/Austauschs
progress = {"active": False, "frac": 0.0, "error": None, "done": False}


def is_frozen():
    return getattr(sys, "frozen", False)


def _ver_tuple(v):
    out = []
    for part in str(v).lstrip("vV").strip().split("."):
        digits = "".join(ch for ch in part if ch.isdigit())
        out.append(int(digits) if digits else 0)
    return tuple(out) if out else (0,)


def cleanup_old():
    """Entfernt die alte EXE nach einem erfolgten Update (beim nächsten Start)."""
    try:
        old = sys.executable + ".old"
        if os.path.exists(old):
            os.remove(old)
    except Exception:
        pass


def _check(current_version):
    try:
        req = urllib.request.Request(API_LATEST, headers=_HEADERS)
        with urllib.request.urlopen(req, timeout=8) as r:
            data = json.load(r)
        tag = data.get("tag_name") or ""
        url = None
        for asset in data.get("assets", []):
            if str(asset.get("name", "")).lower().endswith(".exe"):
                url = asset.get("browser_download_url")
                break
        newer = _ver_tuple(tag) > _ver_tuple(current_version)
        status.update(checked=True, available=bool(newer and url),
                      version=str(tag).lstrip("vV"), url=url)
    except Exception:
        status.update(checked=True, available=False)


def check_async(current_version):
    """Startet den Versions-Check im Hintergrund (blockiert das Spiel nicht)."""
    threading.Thread(target=_check, args=(current_version,), daemon=True).start()


def _do_apply(url):
    try:
        exe = sys.executable
        new_path = exe + ".new"
        req = urllib.request.Request(url, headers=_HEADERS)
        with urllib.request.urlopen(req, timeout=60) as r:
            total = int(r.headers.get("Content-Length", 0) or 0)
            got = 0
            with open(new_path, "wb") as f:
                while True:
                    chunk = r.read(65536)
                    if not chunk:
                        break
                    f.write(chunk)
                    got += len(chunk)
                    if total:
                        progress["frac"] = got / total
        # Laufende EXE beiseite schieben (auf Windows erlaubt), neue an ihre Stelle
        old_path = exe + ".old"
        if os.path.exists(old_path):
            try:
                os.remove(old_path)
            except Exception:
                pass
        os.replace(exe, old_path)
        os.replace(new_path, exe)
        progress["frac"] = 1.0
        subprocess.Popen([exe])      # neue Version starten
        progress["done"] = True      # Spiel beendet sich -> neue läuft
    except Exception as e:
        progress["error"] = str(e)
        progress["active"] = False


def apply_update(url=None):
    """Lädt das Update und tauscht die EXE (im Hintergrund-Thread)."""
    url = url or status.get("url")
    if not is_frozen():
        progress.update(active=False, error="Update nur in der EXE-Version möglich.")
        return
    if not url:
        progress.update(active=False, error="Kein Download verfügbar.")
        return
    progress.update(active=True, frac=0.0, error=None, done=False)
    threading.Thread(target=_do_apply, args=(url,), daemon=True).start()
