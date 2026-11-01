"""Sbazar – www.sbazar.cz (Seznam).

Sbazar načítá inzeráty přes své JSON rozhraní, které volá i web
(adresa níže je můj odhad z dřívějška – první běh ověří, jinak
spadneme na čtení HTML výsledků hledání).
"""
import re
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from common import UA, fetch, parse_price, PAUSE
from config import HLEDAT, PREKLEPY

API = "https://www.sbazar.cz/api/v1/items/search"
WEB = "https://www.sbazar.cz/"
ITEM_RE = re.compile(r"/(\d{6,})-")


def _via_api(q):
    import time
    time.sleep(PAUSE)
    r = requests.get(API, params={"phrase": q, "limit": 50, "sort": "newest"},
                     headers={"User-Agent": UA}, timeout=30)
    if r.status_code != 200:
        print(f"  sbazar api '{q}' -> HTTP {r.status_code}")
        return None
    data = r.json()
    items = data.get("results") or data.get("items") or []
    rows = []
    for it in items:
        iid = str(it.get("id") or "")
        if not iid:
            continue
        rows.append({
            "id": iid,
            "url": f"https://www.sbazar.cz/{it.get('seo_name') or ''}/detail/{iid}",
            "nazev": it.get("name"),
            "cena": it.get("price") if isinstance(it.get("price"), int) else parse_price(str(it.get("price"))),
            "lokalita": (it.get("locality") or {}).get("municipality") if isinstance(it.get("locality"), dict) else None,
            "popis": (it.get("description") or "")[:600],
            "typ": "koupim" if re.match(r"\s*koup[ií]m", it.get("name") or "", re.I) else "prodam",
        })
    return rows


def _via_html(q):
    html = fetch(urljoin(WEB, "hledej/"), params={"q": q})
    if not html:
        return []
    soup = BeautifulSoup(html, "html.parser")
    rows, seen = [], set()
    for a in soup.find_all("a", href=ITEM_RE):
        iid = ITEM_RE.search(a["href"]).group(1)
        title = a.get_text(" ", strip=True)
        if iid in seen or not title:
            continue
        seen.add(iid)
        box = a.parent.parent if a.parent and a.parent.parent else a
        price_el = box.find(string=re.compile(r"Kč"))
        rows.append({
            "id": iid, "url": urljoin(WEB, a["href"]), "nazev": title,
            "cena": parse_price(price_el) if price_el else None,
            "lokalita": None, "popis": box.get_text(" ", strip=True)[:600],
            "typ": "koupim" if re.match(r"\s*koup[ií]m", title, re.I) else "prodam",
        })
    return rows


def collect():
    rows = []
    for q in HLEDAT + PREKLEPY:
        try:
            found = _via_api(q)
        except Exception as e:  # JSON nesedí → HTML
            print(f"  sbazar api '{q}' chyba: {e}")
            found = None
        if found is None:
            found = _via_html(q)
        print(f"  sbazar '{q}': {len(found)}")
        rows.extend(found)
    return rows
