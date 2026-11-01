"""Sběr jen Aukro + Annonce – spouští se z počítače uživatele (ty dva weby
blokují GitHub). Výstup: JSON soubor s inzeráty, který pak collectors/import_local.py
nahraje do databáze v repozitáři.

Použití:  python run_local.py VYSTUP.json
"""
import json
import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import annonce, aukro  # noqa: E402

out = Path(sys.argv[1] if len(sys.argv) > 1 else "local.json")
result = {}
for name, mod in (("aukro", aukro), ("annonce", annonce)):
    try:
        rows = mod.collect()
        result[name] = {"rows": rows, "error": None}
        print(f"{name}: {len(rows)}")
    except Exception as e:
        traceback.print_exc()
        result[name] = {"rows": [], "error": str(e)[:300]}
out.write_text(json.dumps(result, ensure_ascii=False), encoding="utf-8")
print("zapsáno", out)
