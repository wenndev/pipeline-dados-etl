from pathlib import Path
from typing import Any

import pandas as pd

from pipeline_dados.logging import get_logger

logger = get_logger("parquet")


def save_parquet(data: Any, path: str | Path) -> Path:
    output_path = Path(path)

    if output_path.suffix != ".parquet":
        output_path = output_path.with_suffix(".parquet")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    if isinstance(data, pd.DataFrame):
        dataframe = data
    elif isinstance(data, dict):
        dataframe = pd.DataFrame([data])
    else:
        dataframe = pd.DataFrame(data)

    dataframe.to_parquet(output_path, index=False)
    logger.info("Parquet saved at %s", output_path)

    return output_path

