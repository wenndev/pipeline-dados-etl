import pandas as pd

from pipeline_dados.storage.parquet import save_parquet


def test_save_parquet_creates_file(tmp_path):
    output_path = save_parquet([{"coin": "bitcoin", "price": 1}], tmp_path / "markets")

    assert output_path.name == "markets.parquet"
    assert output_path.exists()

    dataframe = pd.read_parquet(output_path)
    assert dataframe.to_dict(orient="records") == [{"coin": "bitcoin", "price": 1}]
