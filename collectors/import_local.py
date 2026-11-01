"""Nahraje výstup run_local.py (JSON z počítače uživatele) do data/inzeraty.sqlite.

Použití:  python import_local.py VYSTUP.json
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import db, log_error, save  # noqa: E402

data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
con = db()
for name, part in data.items():
    if part.get("error"):
        log_error(con, name, part["error"])
        print(f"{name}: chyba – {part['error']}")
        continue
    new = save(con, name, part["rows"])
    print(f"{name}: {len(part['rows'])} nalezeno, {new} nových")
