from __future__ import annotations

from pathlib import Path

import duckdb


def validate(database: str | Path) -> dict:
    con = duckdb.connect(str(database), read_only=True)
    rows = con.execute("SELECT COUNT(*) FROM fato_comex_ncm").fetchone()[0]
    null_keys = con.execute("""
        SELECT COUNT(*) FROM fato_comex_ncm
        WHERE CO_ANO IS NULL OR CO_MES IS NULL OR CO_PAIS IS NULL OR fluxo IS NULL
    """).fetchone()[0]
    bad_months = con.execute("SELECT COUNT(*) FROM fato_comex_ncm WHERE CO_MES NOT BETWEEN 1 AND 12").fetchone()[0]
    negative_values = con.execute("SELECT COUNT(*) FROM fato_comex_ncm WHERE VL_FOB < 0 OR KG_LIQUIDO < 0").fetchone()[0]
    con.close()
    result = {"rows": rows, "null_keys": null_keys, "bad_months": bad_months, "negative_values": negative_values}
    if any(result[key] for key in ["null_keys", "bad_months", "negative_values"]):
        raise ValueError(f"falha de qualidade: {result}")
    return result
