from __future__ import annotations

from pathlib import Path

import duckdb
import pandas as pd

EXPECTED = ["CO_ANO", "CO_MES", "CO_NCM", "CO_UNID", "CO_PAIS", "SG_UF_NCM", "CO_VIA", "CO_URF", "QT_ESTAT", "KG_LIQUIDO", "VL_FOB"]


def read_comex_csv(path: str | Path) -> pd.DataFrame:
    frame = pd.read_csv(path, sep=";", encoding="latin1", dtype=str)
    missing = [column for column in EXPECTED if column not in frame.columns]
    if missing:
        raise ValueError(f"colunas obrigatórias ausentes em {path}: {missing}")
    for column in ["CO_ANO", "CO_MES"]:
        frame[column] = pd.to_numeric(frame[column], errors="raise", downcast="integer")
    for column in ["QT_ESTAT", "KG_LIQUIDO", "VL_FOB", "VL_FRETE", "VL_SEGURO"]:
        if column in frame:
            frame[column] = pd.to_numeric(frame[column].str.replace(",", ".", regex=False), errors="coerce").fillna(0)
    return frame


def transform(input_dir: str | Path, output_dir: str | Path, year: int | None = None) -> dict:
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    files = sorted(input_path.glob("*.csv"))
    if year is not None:
        files = [path for path in files if str(year) in path.name]
    if not files:
        raise FileNotFoundError(f"nenhum CSV encontrado em {input_path}")

    frames = []
    for path in files:
        flow = "IMP" if path.name.upper().startswith("IMP") else "EXP"
        frame = read_comex_csv(path)
        frame["fluxo"] = flow
        frames.append(frame)
    detailed = pd.concat(frames, ignore_index=True)
    staged = output_path / "staged_comex.parquet"
    detailed.to_parquet(staged, index=False, compression="zstd")

    con = duckdb.connect(str(output_path / "comex.duckdb"))
    con.register("detailed_df", detailed)
    con.execute("CREATE OR REPLACE TABLE fato_comex_ncm AS SELECT * FROM detailed_df")
    con.execute("""
        CREATE OR REPLACE TABLE mart_comercio_anual_pais AS
        SELECT CO_ANO AS ano, fluxo, CO_PAIS AS codigo_pais,
               SUM(VL_FOB) AS valor_fob_usd, SUM(KG_LIQUIDO) AS kg_liquido,
               COUNT(*) AS linhas_origem
        FROM fato_comex_ncm
        GROUP BY 1, 2, 3
        ORDER BY 1, 2, valor_fob_usd DESC
    """)
    con.execute("""
        CREATE OR REPLACE TABLE mart_ranking_parceiros AS
        WITH anual AS (SELECT * FROM mart_comercio_anual_pais),
        ranking AS (
          SELECT *, ROW_NUMBER() OVER (PARTITION BY ano, fluxo ORDER BY valor_fob_usd DESC) AS ranking_anual
          FROM anual
        )
        SELECT *, SUM(valor_fob_usd) OVER (PARTITION BY fluxo, codigo_pais ORDER BY ano ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS valor_fob_acumulado_usd
        FROM ranking
    """)
    con.execute("COPY mart_comercio_anual_pais TO ? (FORMAT PARQUET, COMPRESSION ZSTD)", [str(output_path / "mart_comercio_anual_pais.parquet")])
    con.execute("COPY mart_ranking_parceiros TO ? (FORMAT PARQUET, COMPRESSION ZSTD)", [str(output_path / "mart_ranking_parceiros.parquet")])
    row_count = con.execute("SELECT COUNT(*) FROM fato_comex_ncm").fetchone()[0]
    con.close()
    return {"rows": row_count, "staged": str(staged), "output_dir": str(output_path)}
