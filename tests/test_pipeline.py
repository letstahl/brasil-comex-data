from pathlib import Path

import pandas as pd

from brasil_comex.transform import transform
from brasil_comex.validate import validate


def test_transform_and_validate(tmp_path: Path):
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    frame = pd.DataFrame({
        "CO_ANO": [2023, 2023, 2024], "CO_MES": [1, 2, 1], "CO_NCM": ["01012100"] * 3,
        "CO_UNID": ["10"] * 3, "CO_PAIS": ["249", "249", "105"], "SG_UF_NCM": ["SP"] * 3,
        "CO_VIA": ["1"] * 3, "CO_URF": ["817800"] * 3, "QT_ESTAT": ["1", "2", "3"],
        "KG_LIQUIDO": [10, 20, 30], "VL_FOB": [100, 200, 300]
    })
    frame.to_csv(input_dir / "EXP_2023.csv", sep=";", index=False, encoding="latin1")
    result = transform(input_dir, output_dir)
    assert result["rows"] == 3
    quality = validate(output_dir / "comex.duckdb")
    assert quality["rows"] == 3
    annual = pd.read_parquet(output_dir / "mart_comercio_anual_pais.parquet")
    assert annual["valor_fob_usd"].sum() == 600
