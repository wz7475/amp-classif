from typing import List, Tuple

import pandas as pd
from Bio import SeqIO

"""
requires package: amp
from https://github.com/szczurek-lab/hydramp
"""
from amp.inference.filtering import amino_based_filtering
from classif.config import Config


def preprocess_candidates(df: pd.DataFrame, positive_path: str = "resources/hydramp_data/unlabelled_positive.csv",
                          verbose: bool = True) -> pd.DataFrame:
    size_before = df.shape[0]
    df = amino_based_filtering(positive_path, df)
    if verbose:
        print(f"Total number of sequences: {size_before}; after filtering: {df.shape[0]}")
    return df


def clean_ampscanner_preds(df: pd.DataFrame) -> pd.DataFrame:
    df.rename({
        "SeqID": "id",
        "Prediction_Class": "prediction",
        "Prediction_Probability": "score",
    }, axis="columns", inplace=True)
    df["prediction"] = df["prediction"].str.replace("Non-AMP\*", "non-AMP") \
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


def setup_ampscanner(input_path: str) -> Tuple[List[List[int]], List[str], List[str], List[str]]:
    X_test, warn, ids, seqs = [], [], [], []
    aa2int = {aa: i for i, aa in enumerate(Config.AMINO_ACIDS)}
    for s in SeqIO.parse(input_path, "fasta"):
        if len(s.seq) < Config.AMPSCANNER_MIN_LENGTH or len(s.seq) > Config.AMPSCANNER_MAX_LENGTH:
            warn.append("*")
        else:
            warn.append("")
            ids.append(str(s.id))
            seqs.append(str(s.seq))
            X_test.append([aa2int[aa] for aa in s.seq.upper()])
    return X_test, warn, ids, seqs
