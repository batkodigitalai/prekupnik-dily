"""Spouštěč: projde všechny zdroje, uloží do SQLite, zapíše stav do data/STAV.md."""
import sys
import traceback
from datetime import datetime, timezone, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import annonce, aukro, bazos, sbazar  # noqa: E402
from common import db, log_error, save  # noqa: E402

ZDROJE = {"bazos": bazos, "sbazar": sbazar, "aukro": aukro, "annonce": annonce}


def main():
    con = db()
    summary = []
    for name, mod in ZDROJE.items():
        print(f"== {name}")
        try:
            rows = mod.collect()
            new = save(con, name, rows)
            summary.append((name, len(rows), new, ""))
        except Exception as e:
            traceback.print_exc()
            log_error(con, name, e)
            summary.append((name, 0, 0, str(e)[:120]))

    total = con.execute("SELECT COUNT(*) FROM inzeraty").fetchone()[0]
    with_price = con.execute("SELECT COUNT(*) FROM inzeraty WHERE cena IS NOT NULL").fetchone()[0]
    koupim = con.execute("SELECT COUNT(*) FROM inzeraty WHERE typ='koupim'").fetchone()[0]
    prodano = con.execute("SELECT COUNT(*) FROM inzeraty WHERE typ='prodano'").fetchone()[0]
    now = datetime.now(timezone(timedelta(hours=1))).strftime("%d. %m. %Y %H:%M")

    lines = [
        "# Stav sběrače – autodíly", "",
        f"Poslední běh: {now} (čas Praha)", "",
        "| Zdroj | Nalezeno v běhu | Nových | Chyba |", "|---|---|---|---|",
    ]
    for name, n, new, err in summary:
        lines.append(f"| {name} | {n} | {new} | {err} |")
    lines += [
        "",
        f"Celkem v databázi: **{total}** inzerátů, z toho s cenou {with_price}, "
        f"„koupím“ {koupim}, ukončené aukce s dosaženou cenou {prodano}.",
        "",
        "Databáze: `data/inzeraty.sqlite`. Hlášení podhodnocených kusů začne, "
        "až bude dost referenčních cen (cíl: 14 dní sběru).",
    ]
    Path(__file__).resolve().parent.parent.joinpath("data", "STAV.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
