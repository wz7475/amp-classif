import pandas as pd


def clean_stm_preds(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = df.columns.str.lower()
    df.rename({"predictions": "prediction"}, inplace=True)
    df["prediction"] = df["prediction"].str.replace("Non-AMP", "non-AMP")
    df["prediction_num"] = (df["prediction"] == "AMP").astype(int)
    return df
