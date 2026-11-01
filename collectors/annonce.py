"""Annonce – www.annonce.cz, rubrika autodíly. Zkušební zdroj: po týdnu
rozhodneme, jestli tam vůbec něco nového chodí."""
import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from common import fetch, parse_price
from config import HLEDAT

BASE = "https://www.annonce.cz/"
ITEM_RE = re.compile(r"/[a-z0-9-]+-(\d{6,})\.html")


def collect():
    rows, seen = [], set()
    for q in HLEDAT:
        html = fetch(urljoin(BASE, "hledat/"), params={"q": q, "kategorie": "auto-moto"})
        if not html:
            continue
        soup = BeautifulSoup(html, "html.parser")
        n = 0
        for a in soup.find_all("a", href=ITEM_RE):
            iid = ITEM_RE.search(a["href"]).group(1)
            title = a.get_text(" ", strip=True)
            if iid in seen or not title:
                continue
            seen.add(iid)
            box = a.parent.parent if a.parent and a.parent.parent else a
            price_el = box.find(string=re.compile(r"Kč"))
            rows.append({
                "id": iid, "url": urljoin(BASE, a["href"]), "nazev": title,
                "cena": parse_price(price_el) if price_el else None,
                "lokalita": None, "popis": box.get_text(" ", strip=True)[:600],
                "typ": "koupim" if re.match(r"\s*koup[ií]m", title, re.I) else "prodam",
            })
            n += 1
        print(f"  annonce '{q}': {n}")
    return rows
