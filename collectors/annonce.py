"""Annonce – rubrika Náhradní díly osobní vozy (ověřeno 1. 11. 2026 v prohlížeči).

Čteme výpis rubriky (nejnovější první), 4 stránky nabídek + 2 stránky poptávek.
Každý inzerát má pole Nabídka/Poptávka – poptávky = 'koupim'.
"""
import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from common import fetch, parse_price

BASE = "https://www.annonce.cz/"
LIST = "https://www.annonce.cz/nahradni-dily-osobni-vozy$18.html"
ITEM_RE = re.compile(r"/inzerat/.*-(\d{6,})-[a-z0-9]+\.html")


def _parse(html):
    soup = BeautifulSoup(html, "html.parser")
    rows = []
    for box in soup.select("div.box.ext-item"):
        a = box.select_one("h2 a")
        if not a or not ITEM_RE.search(a.get("href", "")):
            continue
        iid = ITEM_RE.search(a["href"]).group(1)
        typ_el = box.select_one(".request-type")
        typ = "koupim" if typ_el and "popt" in typ_el.get_text().lower() else "prodam"
        price_el = box.select_one(".mini-sticker")
        attrs = {}
        for tr in box.select("table.attrs tr"):
            th, td = tr.find("th"), tr.find("td")
            if th and td and td.get_text(strip=True):
                attrs[th.get_text(strip=True).rstrip(":")] = td.get_text(strip=True)
        desc = box.select_one(".ad-desc")
        popis = " | ".join(f"{k}: {v}" for k, v in attrs.items())
        if desc:
            popis = (popis + " | " if popis else "") + desc.get_text(" ", strip=True)
        rows.append({
            "id": iid, "url": urljoin(BASE, a["href"]), "nazev": a.get_text(" ", strip=True),
            "cena": parse_price(price_el.get_text()) if price_el else None,
            "lokalita": attrs.get("Lokalita"), "popis": popis[:600], "typ": typ,
        })
    return rows


def collect():
    rows = []
    for nab, pages in (("1", 4), ("0", 2)):
        for page in range(1, pages + 1):
            html = fetch(LIST, params={"nabidkovy": nab, "page": page})
            if not html:
                break
            found = _parse(html)
            print(f"  annonce nabidkovy={nab} p{page}: {len(found)}")
            if not found:
                break
            rows.extend(found)
    return rows
