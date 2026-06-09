import pandas as pd
from pathlib import Path

class DataStore:

    def save_parquet(
        self,
        records,
        filename
    ):

        df = pd.DataFrame(records)

        path = Path(
            f"data/parquet/{filename}.parquet"
        )

        df.to_parquet(path)

        return str(path)