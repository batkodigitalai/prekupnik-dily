"""Bazoš – auto.bazos.cz (autodíly, prodám i koupím).

Čte veřejné výsledky vyhledávání. Rozložení stránky Bazoš občas mění,
proto parser stojí hlavně na stabilním vzoru adresy /inzerat/<id>/…
a selektory tříd jsou jen pomocné. První běh na GitHubu ukáže,
jestli parser sedí – viz tabulka `behy`.
"""
import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from common import fetch, parse_price
from config import HLEDAT, PREKLEPY, LOKALITA_PSC, OKRUH_KM

BASE = "https://auto.bazos.cz/"
INZERAT_RE = re.compile(r"/inzerat/(\d+)/")


def _parse_listing(html, typ):
    soup = BeautifulSoup(html, "html.parser")
    rows, seen = [], set()
    for a in soup.find_all("a", href=INZERAT_RE):
        m = INZERAT_RE.search(a["href"])
        iid = m.group(1)
        title = a.get_text(" ", strip=True)
        if iid in seen or not title:
            continue
        seen.add(iid)
        box = a
        for _ in range(4):  # vylézt k obalu inzerátu
            if box.parent is None:
                break
            box = box.parent
            if box.name == "div" and "inzeraty" in " ".join(box.get("class", [])):
                break
        text = box.get_text(" ", strip=True)
        price_el = box.find(class_=re.compile("cena"))
        lok_el = box.find(class_=re.compile("lok"))
        popis_el = box.find(class_=re.compile("popis"))
        rows.append(
            {
                "id": iid,
                "url": urljoin(BASE, a["href"]),
                "nazev": title,
                "cena": parse_price(price_el.get_text() if price_el else ""),
                "lokalita": lok_el.get_text(" ", strip=True) if lok_el else None,
                "popis": (popis_el.get_text(" ", strip=True) if popis_el else text)[:600],
                "typ": typ,
            }
        )
    return rows


def collect():
    rows = []
    for q in HLEDAT + PREKLEPY:
        html = fetch(
            BASE,
            params={"hledat": q, "hlokalita": LOKALITA_PSC, "humkreis": OKRUH_KM, "cenaod": "", "cenado": ""},
        )
        if not html:
            continue
        found = _parse_listing(html, "prodam")
        # Bazoš dává „koupím“ do stejné rubriky; poznáme je podle textu názvu
        for r in found:
            if re.match(r"\s*(koupim|koupím|sháním|shanim|hledám|hledam)\b", r["nazev"], re.I):
                r["typ"] = "koupim"
        print(f"  bazos '{q}': {len(found)}")
        rows.extend(found)
    return rows
