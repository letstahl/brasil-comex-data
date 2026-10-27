from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable
from datetime import datetime, timezone
from pathlib import Path

import requests
import yaml


def load_config(path: str | Path = "config/default.yaml") -> dict:
    with open(path, encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def download_file(url: str, destination: Path, timeout: int = 120) -> dict:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(destination.suffix + ".part")
    with requests.get(url, stream=True, timeout=timeout) as response:
        response.raise_for_status()
        with temporary.open("wb") as handle:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    handle.write(chunk)
    temporary.replace(destination)
    return {
        "url": url,
        "path": str(destination),
        "sha256": sha256_file(destination),
        "bytes": destination.stat().st_size,
        "captured_at_utc": datetime.now(timezone.utc).isoformat(),
    }


def ingest(year: int, flows: Iterable[str], config_path: str | Path = "config/default.yaml") -> list[dict]:
    config = load_config(config_path)
    source = config["source"]
    raw_dir = Path(config["pipeline"]["raw_dir"]) / f"year={year}"
    records = []
    for flow in flows:
        flow = flow.upper()
        if flow not in {"EXP", "IMP"}:
            raise ValueError("flow deve ser EXP ou IMP")
        template = source["export_template"] if flow == "EXP" else source["import_template"]
        filename = template.format(year=year)
        url = f"{source['base_url'].rstrip('/')}/{filename}"
        metadata = download_file(url, raw_dir / filename)
        metadata.update({"year": year, "flow": flow, "source": source["provider"]})
        records.append(metadata)
    manifest_path = raw_dir / "manifest.json"
    manifest_path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return records
