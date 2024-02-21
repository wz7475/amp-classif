from typing import Tuple, List

import pandas as pd
from Bio import SeqIO

from classif.shared_config import Config as SharedConfig
from classif.ampscannerv2.config import Config as AmpscannerConfig


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


def setup_ampscanner(input_path: str) -> Tuple[List[List[int]], List[str], List[str], List[str]]:
    X_test, warn, ids, seqs = [], [], [], []
    aa2int = {aa: i for i, aa in enumerate(SharedConfig.AMINO_ACIDS)}
    for s in SeqIO.parse(input_path, "fasta"):
        if len(s.seq) < AmpscannerConfig.AMPSCANNER_MIN_LENGTH or len(s.seq) > AmpscannerConfig.AMPSCANNER_MAX_LENGTH:
            warn.append("*")
        else:
            warn.append("")
            ids.append(str(s.id))
            seqs.append(str(s.seq))
            X_test.append([aa2int[aa] for aa in s.seq.upper()])
    return X_test, warn, ids, seqs
