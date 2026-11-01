"""Aukro – aukro.cz/vysledky-vyhledavani?text=… (ověřeno 1. 11. 2026: výsledky
jsou přímo v HTML jako <a class="item-card" href="/nazev-<id>">).

Z prvního běhu na GitHubu přišlo HTTP 403 – zčásti špatná adresa, zčásti
možná blokace serverových IP. Tento běh to rozhodne. Ukončené aukce
(skutečně dosažené ceny) zatím nečteme – doplníme, až bude jasné, že nás
Aukro z GitHubu vůbec pustí.
"""
import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from common import fetch, parse_price
from config import HLEDAT, PREKLEPY

BASE = "https://aukro.cz/"
SEARCH = "https://aukro.cz/vysledky-vyhledavani"
ITEM_RE = re.compile(r"-(\d{7,})$")


def _parse(html):
    soup = BeautifulSoup(html, "html.parser")
    rows, seen = [], set()
    for a in soup.select("a.item-card[href]"):
        href = a["href"].split("?")[0]
        m = ITEM_RE.search(href)
        if not m or m.group(1) in seen:
            continue
        seen.add(m.group(1))
        text = a.get_text(" ", strip=True)
        # název = text před „Žádný příhoz“ / cenou; bereme první smysluplný řádek
        title = re.split(r"\s+(Žádný příhoz|\d[\d\s]*Kč)", text)[0]
        title = re.sub(r"^\s*\d+\s+(Nové|Použité)\s+", "", title).strip()
        # cena: „Kup teď X Kč“ má přednost, jinak aktuální příhoz
        m_kup = re.search(r"Kup teď\s*([\d\s]+)\s*Kč", text)
        m_any = re.search(r"([\d\s]+)\s*Kč", text)
        cena = parse_price(m_kup.group(1) if m_kup else (m_any.group(1) if m_any else ""))
        rows.append({
            "id": m.group(1), "url": urljoin(BASE, href), "nazev": title or text[:80],
            "cena": cena, "lokalita": None, "popis": text[:600],
            "typ": "aukce" if "příhoz" in text else "prodam",
        })
    return rows


def collect():
    rows = []
    for q in HLEDAT + PREKLEPY:
        html = fetch(SEARCH, params={"text": q})
        if not html:
            continue
        found = _parse(html)
        print(f"  aukro '{q}': {len(found)}")
        rows.extend(found)
    return rows
