from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import duckdb
import pandas as pd
import requests

BASE_URL = "https://balanca.mdic.gov.br/balanca/bd/comexstat-bd/ncm"
COUNTRY_TABLE_URL = "https://balanca.mdic.gov.br/balanca/bd/tabelas/TABELAS_AUXILIARES.xlsx"


def download(url: str, destination: Path) -> dict:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if not destination.exists():
        with requests.get(url, stream=True, timeout=180) as response:
            response.raise_for_status()
            with destination.open("wb") as handle:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        handle.write(chunk)
    digest = hashlib.sha256()
    with destination.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return {
        "url": url,
        "file": destination.name,
        "bytes": destination.stat().st_size,
        "sha256": digest.hexdigest(),
    }


def load_country_dimension(path: Path) -> pd.DataFrame:
    frame = pd.read_excel(path, sheet_name="10", dtype={"CO_PAIS": str})
    return frame[["CO_PAIS", "NO_PAIS", "CO_PAIS_ISOA3"]].rename(
        columns={"CO_PAIS": "codigo_pais", "NO_PAIS": "nome_pais", "CO_PAIS_ISOA3": "pais_iso3"}
    )


def build(years: list[int], output_dir: Path, source_dir: Path) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    source_dir.mkdir(parents=True, exist_ok=True)
    country_xlsx = source_dir / "TABELAS_AUXILIARES.xlsx"
    source_manifest = [download(COUNTRY_TABLE_URL, country_xlsx)]
    country = load_country_dimension(country_xlsx)
    country_csv = output_dir / "dim_pais.csv"
    country.to_csv(country_csv, index=False)
    con = duckdb.connect()
    con.register("country_df", country)
    con.execute("CREATE OR REPLACE TEMP TABLE dim_pais AS SELECT * FROM country_df")
    annual_parts: list[str] = []
    monthly_parts: list[str] = []

    for year in years:
        for flow, prefix in (("EXP", "export"), ("IMP", "import")):
            filename = f"{flow}_{year}.csv"
            url = f"{BASE_URL}/{filename}"
            metadata = download(url, source_dir / filename)
            metadata.update({"year": year, "flow": flow})
            source_manifest.append(metadata)
            csv_path = str(source_dir / filename).replace("'", "''")
            relation = f"read_csv('{csv_path}', delim=';', header=true, encoding='latin-1', all_varchar=true, sample_size=10000)"
            query = f"""
                SELECT
                    TRY_CAST(CO_ANO AS INTEGER) AS ano,
                    TRY_CAST(CO_MES AS INTEGER) AS mes,
                    CAST(CO_PAIS AS VARCHAR) AS codigo_pais,
                    SUM(TRY_CAST(REPLACE(VL_FOB, ',', '.') AS DOUBLE)) AS valor_fob_usd,
                    SUM(TRY_CAST(REPLACE(KG_LIQUIDO, ',', '.') AS DOUBLE)) AS kg_liquido,
                    COUNT(*) AS linhas_origem,
                    '{flow}' AS fluxo
                FROM {relation}
                GROUP BY 1, 2, 3
            """
            monthly_parts.append(f"({query})")
            annual_parts.append(f"SELECT ano, codigo_pais, valor_fob_usd, kg_liquido, linhas_origem, fluxo FROM ({query})")

    monthly_union = " UNION ALL ".join(monthly_parts)
    annual_sql = f"""
        SELECT ano, fluxo, codigo_pais,
               SUM(valor_fob_usd) AS valor_fob_usd,
               SUM(kg_liquido) AS kg_liquido,
               SUM(linhas_origem) AS linhas_origem
        FROM ({monthly_union})
        GROUP BY 1, 2, 3
    """
    monthly_sql = f"""
        SELECT m.ano, m.mes, m.fluxo, m.codigo_pais,
               COALESCE(d.nome_pais, 'País não identificado') AS nome_pais,
               COALESCE(d.pais_iso3, '') AS pais_iso3,
               m.valor_fob_usd, m.kg_liquido, m.linhas_origem
        FROM ({monthly_union}) m
        LEFT JOIN dim_pais d USING (codigo_pais)
        ORDER BY 1, 2, 3, 7 DESC
    """
    annual_enriched = f"""
        SELECT a.ano, a.fluxo, a.codigo_pais,
               COALESCE(d.nome_pais, 'País não identificado') AS nome_pais,
               COALESCE(d.pais_iso3, '') AS pais_iso3,
               a.valor_fob_usd, a.kg_liquido, a.linhas_origem,
               a.valor_fob_usd / NULLIF(SUM(a.valor_fob_usd) OVER (PARTITION BY a.ano, a.fluxo), 0) AS participacao
        FROM ({annual_sql}) a
        LEFT JOIN dim_pais d USING (codigo_pais)
    """
    con.execute(f"COPY ({annual_enriched} ORDER BY ano, fluxo, valor_fob_usd DESC) TO '{output_dir / 'comercio_anual_pais.parquet'}' (FORMAT PARQUET, COMPRESSION ZSTD)")
    con.execute(f"COPY ({annual_enriched} ORDER BY ano, fluxo, valor_fob_usd DESC) TO '{output_dir / 'comercio_anual_pais.csv'}' (HEADER, DELIMITER ',')")
    con.execute(f"COPY ({monthly_sql}) TO '{output_dir / 'comercio_mensal_pais.parquet'}' (FORMAT PARQUET, COMPRESSION ZSTD)")

    ranking_sql = f"""
        SELECT *,
               ROW_NUMBER() OVER (PARTITION BY ano, fluxo ORDER BY valor_fob_usd DESC) AS ranking_anual,
               SUM(valor_fob_usd) OVER (PARTITION BY fluxo, codigo_pais ORDER BY ano ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS valor_fob_acumulado_usd
        FROM ({annual_enriched})
    """
    con.execute(f"COPY ({ranking_sql} ORDER BY ano, fluxo, ranking_anual) TO '{output_dir / 'ranking_parceiros.csv'}' (HEADER, DELIMITER ',')")
    con.execute(f"COPY ({ranking_sql} ORDER BY ano, fluxo, ranking_anual) TO '{output_dir / 'ranking_parceiros.parquet'}' (FORMAT PARQUET, COMPRESSION ZSTD)")

    saldo_sql = f"""
        SELECT ano, codigo_pais, nome_pais, pais_iso3,
               SUM(CASE WHEN fluxo = 'EXP' THEN valor_fob_usd ELSE 0 END) AS exportacoes_usd,
               SUM(CASE WHEN fluxo = 'IMP' THEN valor_fob_usd ELSE 0 END) AS importacoes_usd,
               SUM(CASE WHEN fluxo = 'EXP' THEN valor_fob_usd ELSE -valor_fob_usd END) AS saldo_usd
        FROM ({annual_enriched})
        GROUP BY 1, 2, 3, 4
    """
    con.execute(f"COPY ({saldo_sql} ORDER BY ano, saldo_usd DESC) TO '{output_dir / 'saldo_comercial_pais.csv'}' (HEADER, DELIMITER ',')")
    con.close()

    catalog = {
        "dataset": "Brasil Comércio Exterior Dados",
        "version": "2024.1",
        "source": "MDIC/SECEX Comex Stat",
        "source_url": "https://www.gov.br/mdic/pt-br/assuntos/comercio-exterior/estatisticas/base-de-dados-bruta",
        "period_start": min(years),
        "period_end": max(years),
        "years": years,
        "flows": ["EXP", "IMP"],
        "grain": "ano, fluxo e país para comércio_anual_pais; ano, mês, fluxo e país para comércio_mensal_pais",
        "metrics": ["valor_fob_usd", "kg_liquido", "participacao"],
        "updated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_files": source_manifest,
        "notes": [
            "A camada inicial cobre 2023 e 2024.",
            "Os valores são estatísticas agregadas de bens.",
            "O ano mais recente pode estar sujeito a revisões da fonte.",
            "A API não foi usada nesta carga; os arquivos anuais abertos foram processados diretamente."
        ]
    }
    (output_dir / "catalog.json").write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return catalog


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--years", nargs="+", type=int, default=[2023, 2024])
    parser.add_argument("--output-dir", type=Path, default=Path("data/curated"))
    parser.add_argument("--source-dir", type=Path, default=Path("/tmp/brasil-comex-source"))
    args = parser.parse_args()
    result = build(args.years, args.output_dir, args.source_dir)
    print(json.dumps({"output_dir": str(args.output_dir), "years": result["years"], "flows": result["flows"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
