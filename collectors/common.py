"""Společné funkce sběrače: stahování, databáze, normalizace."""
import re
import sqlite3
import time
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

import requests

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "inzeraty.sqlite"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
PAUSE = 2.5  # sekundy mezi požadavky – slušné tempo, ať nás neblokují


def fetch(url, params=None, pause=PAUSE):
    """Stáhne stránku, vrátí HTML text nebo None při chybě."""
    time.sleep(pause)
    try:
        r = requests.get(url, params=params, headers={"User-Agent": UA, "Accept-Language": "cs"}, timeout=30)
        if r.status_code != 200:
            print(f"  ! {url} -> HTTP {r.status_code}")
            return None
        r.encoding = r.apparent_encoding or "utf-8"
        return r.text
    except requests.RequestException as e:
        print(f"  ! {url} -> {e}")
        return None


def db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.execute(
        """CREATE TABLE IF NOT EXISTS inzeraty (
            zdroj TEXT NOT NULL,
            id TEXT NOT NULL,
            url TEXT,
            nazev TEXT,
            nazev_norm TEXT,
            cena INTEGER,
            lokalita TEXT,
            popis TEXT,
            typ TEXT,              -- prodam / koupim / aukce / prodano
            prvni_videno TEXT,
            posledni_videno TEXT,
            PRIMARY KEY (zdroj, id)
        )"""
    )
    con.execute(
        """CREATE TABLE IF NOT EXISTS behy (
            cas TEXT, zdroj TEXT, nalezeno INTEGER, novych INTEGER, chyba TEXT
        )"""
    )
    return con


def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def normalize(text):
    """Bez diakritiky, malá písmena, jen alfanumerika a mezery."""
    if not text:
        return ""
    t = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    t = re.sub(r"[^a-z0-9 ]+", " ", t.lower())
    return re.sub(r"\s+", " ", t).strip()


def parse_price(text):
    """'12 500 Kč' / '12.500,-' / 'Dohodou' -> int nebo None."""
    if not text:
        return None
    digits = re.sub(r"[^\d]", "", text)
    if not digits:
        return None
    v = int(digits)
    return v if 0 < v < 50_000_000 else None


def save(con, zdroj, rows):
    """Uloží seznam slovníků, vrátí počet nových."""
    ts = now_iso()
    new = 0
    for r in rows:
        cur = con.execute("SELECT 1 FROM inzeraty WHERE zdroj=? AND id=?", (zdroj, r["id"]))
        if cur.fetchone():
            con.execute(
                "UPDATE inzeraty SET posledni_videno=?, cena=COALESCE(?, cena) WHERE zdroj=? AND id=?",
                (ts, r.get("cena"), zdroj, r["id"]),
            )
        else:
            new += 1
            con.execute(
                "INSERT INTO inzeraty VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                (
                    zdroj, r["id"], r.get("url"), r.get("nazev"), normalize(r.get("nazev")),
                    r.get("cena"), r.get("lokalita"), r.get("popis"), r.get("typ", "prodam"), ts, ts,
                ),
            )
    con.execute("INSERT INTO behy VALUES (?,?,?,?,?)", (ts, zdroj, len(rows), new, None))
    con.commit()
    return new


def log_error(con, zdroj, msg):
    con.execute("INSERT INTO behy VALUES (?,?,?,?,?)", (now_iso(), zdroj, 0, 0, str(msg)[:500]))
    con.commit()
