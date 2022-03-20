import math
from pathlib import Path
from typing import Any, Iterable, List, Tuple, Union

import itertools
import pandas as pd
from Bio import SeqIO


def split_into_chunks(iterable: Iterable[Any], chunk_size: int) -> Iterable[Tuple[Any]]:
    tmp = iter(iterable)
    return iter(lambda: tuple(itertools.islice(tmp, chunk_size)), ())


def limit_sequences(sequences: Iterable[str], min_length: int = -math.inf, max_length: int = math.inf) -> List[str]:

    assert 0 < min_length <= max_length
    return list(itertools.chain.from_iterable((
        pair for pair in split_into_chunks(sequences, 2)
        if min_length <= len(pair[1]) <= max_length)
    ))


def ensure_consistency(predictions_df: pd.DataFrame, ground_truth_df: pd.DataFrame) -> None:
    predictions_df.dropna(subset=["prediction_num"], inplace=True)
    ground_truth_df.drop(ground_truth_df.index.difference(predictions_df.index), axis="rows", inplace=True)


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
    df["prediction"] = df["Type"].map({"PPV": "AMP", "NPV": "non-AMP"})
    df["prediction_num"] = (df["prediction"] == "AMP").astype(int)
    df.columns = map(lambda x: x.lower().replace(" ", "_"), df.columns)
    return df


def clean_amplify_preds(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = df.columns.str.lower()
    df.rename({"probability_score": "score"}, axis="columns", inplace=True)
    df["prediction_num"] = (df["prediction"] == "AMP").astype(int)
    return df


def clean_ampgram_preds(df: pd.DataFrame) -> pd.DataFrame:
    if df.shape[1] > 2:
        df.drop("Unnamed: 0", axis="columns", inplace=True)
    df.rename({
        "seq_name": "id",
        "probability": "score"
    }, axis="columns", inplace=True)
    df["prediction_num"] = (df["score"] > 0.5).astype("int")
    df["prediction"] = df["prediction_num"].map({1: "AMP", 0: "non-AMP"})
    return df


def clean_ampscanner_preds(df: pd.DataFrame) -> pd.DataFrame:
    df.rename({
        "SeqID": "id",
        "Prediction_Class": "prediction",
        "Prediction_Probability": "score",
    }, axis="columns", inplace=True)
    df["prediction"] = df["prediction"].str.replace("Non-AMP\*", "non-AMP")\
        .replace("Non-AMP", "non-AMP").replace("AMP*", "AMP")
    df["prediction_num"] = (df["prediction"] == "AMP").astype(int)
    df.columns = df.columns.str.lower()
    return df


def clean_stm_preds(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = df.columns.str.lower()
    df.rename({"predictions": "prediction"}, inplace=True)
    df["prediction"] = df["prediction"].str.replace("Non-AMP", "non-AMP")
    df["prediction_num"] = (df["prediction"] == "AMP").astype(int)
    return df
