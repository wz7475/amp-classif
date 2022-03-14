from pathlib import Path

import itertools
import pandas as pd
from Bio import SeqIO

from typing import Any, Iterable, Tuple, Union


def split_into_chunks(iterable: Iterable[Any], chunk_size: int) -> Iterable[Tuple[Any]]:
    tmp = iter(iterable)
    return iter(lambda: tuple(itertools.islice(tmp, chunk_size)), ())


def fasta2csv(path: Union[str, Path], verbose: bool = True) -> None:
    df = pd.DataFrame(((item.id, "".join(amncd for amncd in item.seq))
                       for item in SeqIO.parse(path, "fasta")),
                      columns=["name", "sequence"])
    out = str(path).replace(".fasta", ".csv")
    df['active'] = 1.0 if str(path).find("high") > 0 else 0.0
    df.to_csv(out, index=False)
    if verbose:
        print(f"saved csv to: {out}; containing {df.shape[0]} sequences")


def clean_dbaasp_preds(df: pd.DataFrame) -> pd.DataFrame:
    df = pd.concat((df, df['Predictive value (Type)'].str.split(" ", expand=True)), axis=1)\
        .rename(columns={0: "Predictive value", 1: "Type"})\
        .drop("Predictive value (Type)", axis=1)
    df["Type"] = df["Type"].str.strip(to_strip="()")
    df["Class"].map({"Active": 1.0, "Not Active": 0.0}).astype("float64")
    df.columns = map(lambda x: x.lower().replace(" ", "_"), df.columns)
    return df


def clean_amplify_preds(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = df.columns.str.lower()
    df.rename({"probability_score": "score"}, axis="columns", inplace=True)
    df["prediction_num"] = (df["prediction"] == "AMP").astype("float")
    return df

