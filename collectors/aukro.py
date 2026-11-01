"""Aukro – aukro.cz. Veřejné vyhledávání; u ukončených aukcí bereme
skutečně dosaženou cenu (typ 'prodano') – nejcennější údaj pro referenční ceny.

Aukro je moderní aplikace (hodně JavaScriptu); jestli samotné HTML obsahuje
výsledky, nevím jistě – první běh to ukáže. Záložní cesta je jejich
backend API, jehož adresu si ověříme z prvního běhu (logujeme HTTP stav).
"""
import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from common import fetch, parse_price
from config import HLEDAT, PREKLEPY

BASE = "https://aukro.cz/"
ITEM_RE = re.compile(r"/([a-z0-9-]+)-(\d{7,})$")


def _parse(html, typ):
    soup = BeautifulSoup(html, "html.parser")
    rows, seen = [], set()
    for a in soup.find_all("a", href=True):
        m = ITEM_RE.search(a["href"].split("?")[0])
        if not m:
            continue
        iid = m.group(2)
        title = a.get_text(" ", strip=True)
        if iid in seen or not title or len(title) < 4:
            continue
        seen.add(iid)
        box = a
        for _ in range(5):
            if box.parent is None:
                break
            box = box.parent
            if "Kč" in box.get_text():
                break
        price_el = box.find(string=re.compile(r"Kč"))
        rows.append({
            "id": iid, "url": urljoin(BASE, a["href"]), "nazev": title,
            "cena": parse_price(price_el) if price_el else None,
            "lokalita": None, "popis": box.get_text(" ", strip=True)[:600], "typ": typ,
        })
    return rows


def collect():
    rows = []
    for q in HLEDAT + PREKLEPY:
        html = fetch(urljoin(BASE, "vyhledavani"), params={"text": q, "categoryId": "", "sort": "newest"})
        if html:
            found = _parse(html, "prodam")
            print(f"  aukro '{q}': {len(found)}")
            rows.extend(found)
        # ukončené – skutečné prodejní ceny
        html = fetch(urljoin(BASE, "vyhledavani"), params={"text": q, "ended": "true"})
        if html:
            found = _parse(html, "prodano")
            print(f"  aukro ukončené '{q}': {len(found)}")
            rows.extend(found)
    return rows
