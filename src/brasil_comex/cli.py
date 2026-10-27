from __future__ import annotations

import argparse
import json

from .ingest import ingest
from .transform import transform
from .validate import validate


def main() -> None:
    parser = argparse.ArgumentParser(prog="brasil-comex")
    sub = parser.add_subparsers(dest="command", required=True)

    ingest_parser = sub.add_parser("ingest", help="baixar CSVs anuais do MDIC")
    ingest_parser.add_argument("--year", type=int, required=True)
    ingest_parser.add_argument("--flows", nargs="+", default=["EXP", "IMP"])
    ingest_parser.add_argument("--config", default="config/default.yaml")

    transform_parser = sub.add_parser("transform", help="criar Parquet, DuckDB e marts")
    transform_parser.add_argument("--input", default="data/raw/year=2023")
    transform_parser.add_argument("--output-dir", default="data/mart")
    transform_parser.add_argument("--year", type=int)

    validate_parser = sub.add_parser("validate", help="executar checks de qualidade")
    validate_parser.add_argument("--database", default="data/mart/comex.duckdb")

    args = parser.parse_args()
    if args.command == "ingest":
        result = ingest(args.year, args.flows, args.config)
    elif args.command == "transform":
        result = transform(args.input, args.output_dir, args.year)
    else:
        result = validate(args.database)
    print(json.dumps(result, ensure_ascii=False, indent=2))
