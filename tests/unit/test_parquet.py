import pandas as pd

from storage.parquet import salvar_parquet


def test_salvar_parquet_cria_arquivo(tmp_path):
    caminho_saida = salvar_parquet([{"coin": "bitcoin", "price": 1}], tmp_path / "markets")

    assert caminho_saida.name == "markets.parquet"
    assert caminho_saida.exists()

    dataframe = pd.read_parquet(caminho_saida)
    assert dataframe.to_dict(orient="records") == [{"coin": "bitcoin", "price": 1}]
