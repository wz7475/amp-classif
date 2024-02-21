import itertools
import math
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union

import joblib
import numpy as np
import pandas as pd
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord

"""
requires package: amp
from https://github.com/szczurek-lab/hydramp
"""
from amp.inference.filtering import amino_based_filtering
from classif.config import Config


def split_into_chunks(iterable: Iterable[Any], chunk_size: int) -> Iterable[Tuple[Any]]:
    tmp = iter(iterable)
    return iter(lambda: tuple(itertools.islice(tmp, chunk_size)), ())


def limit_sequences_length(input_fasta: str, min_length: int = -math.inf, max_length: int = math.inf) -> Iterable[SeqRecord]:
    sequences = SeqIO.parse(input_fasta, "fasta")
    return [seq for seq in sequences if min_length <= len(seq.seq) <= max_length]


def tuple2seqrecord(t: Tuple[str, str]) -> SeqRecord:
    return SeqRecord(Seq(t[0]), id=t[1], name=t[1], description="")


def fasta2csv(input_fasta: str, add_class: Optional[int] = None) -> pd.DataFrame:
    df = pd.DataFrame(
        [(s.id, str(s.seq)) for s in SeqIO.parse(input_fasta, "fasta")],
        columns=["id", "sequence"]
    )
    if add_class is not None:
        df["class"] = add_class
    return df


def csv2fasta(input_file: Union[str, Path], output_dir: Union[str, Path], verbose: bool = True) -> None:
    assert str(input_file).endswith(".csv")
    output_file = output_dir/input_file.name.replace(".csv", ".fasta")
    df = pd.read_csv(input_file)
    SeqIO.write(
        (tuple2seqrecord((sequence, str(i))) for i, sequence in enumerate(df["sequence"])),
        output_file, "fasta"
    )
    if verbose:
        print(f"Saved {df.shape[0]} sequences to {output_file}.")


# def candidate2csv(input_file: Union[str, Path], output_dir: Union[str, Path],
#                   positive_path: str = "../resources/hydramp_data/unlabelled_positive.csv", verbose: bool = True) -> None:
#     output_file = output_dir/input_file.name.replace(".joblib", ".fasta")
#     input_file, output_file = str(input_file), str(output_file)
#     assert input_file.endswith(".joblib")
#     raw = joblib.load(input_file)
#     seqs = [item["sequence"] for _, v in raw.items()
#             for item in v["generated_sequences"]]
#     seqs_filtered = amino_based_filtering(positive_path, pd.DataFrame({"sequence": seqs}))["sequence"].to_numpy()
#     if verbose:
#         print(f"All: {len(seqs)}; after chemical filtering: {len(seqs_filtered)}")
#     SeqIO.write(
#         (tuple2seqrecord((sequence, str(i))) for i, sequence in enumerate(seqs_filtered)),
#         output_file, "fasta"
#     )
#     if verbose:
#         print(f"Saved {len(seqs)} sequences to {output_file}.")


def prototypes2csv(input_file: Union[str, Path]) -> pd.DataFrame:
    assert str(input_file).endswith(".joblib")
    return pd.concat(
        (make_df(prototype, data)
         for prototype, data in joblib.load(input_file).items())
    )


def preprocess_candidates(df: pd.DataFrame, positive_path: str = "resources/hydramp_data/unlabelled_positive.csv",
                          verbose: bool = True) -> pd.DataFrame:
    size_before = df.shape[0]
    df = amino_based_filtering(positive_path, df)
    if verbose:
        print(f"Total number of sequences: {size_before}; after filtering: {df.shape[0]}")
    return df


def make_df(prototype: str, candidates: Dict[str, Any]) -> pd.DataFrame:
    df = pd.DataFrame(candidates.pop("generated_sequences", None))
    df["prototype"] = prototype
    return df


def limit_sequences(sequences: Iterable[str], min_length: int = -math.inf, max_length: int = math.inf) -> List[str]:
    assert 0 < min_length <= max_length
    return list(itertools.chain.from_iterable((
        pair for pair in split_into_chunks(sequences, 2)
        if min_length <= len(pair[1]) <= max_length)
    ))


def ensure_consistency(predictions_df: pd.DataFrame, ground_truth_df: pd.DataFrame) -> None:
    predictions_df.dropna(subset=["prediction_num"], inplace=True)
    ground_truth_df.drop(ground_truth_df.index.difference(predictions_df.index), axis="rows", inplace=True)


def clean_dbaasp_preds(df: pd.DataFrame, strain: str) -> pd.DataFrame:
    if strain:
        df = pd.concat((df, df['Predictive value (Type)'].str.split(" ", expand=True)), axis=1) \
            .rename(columns={0: "Predictive value", 1: "Type"}) \
            .drop("Predictive value (Type)", axis=1)
        df["Type"] = df["Type"].str.strip(to_strip="()")
        df["prediction"] = df["Type"].map({"PPV": "AMP", "NPV": "non-AMP"}) if "Human" not in strain \
            else df["Type"].map({"PPV": "non-AMP", "NPV": "AMP"})
    else:
        df.rename({"Seq. ID": "id", "Class": "prediction"}, axis="columns", inplace=True)
        df.drop(df.index[-1], axis="rows", inplace=True)
    df["prediction_num"] = (df["prediction"] == "AMP").astype(int)
    df.columns = map(lambda x: x.lower().replace(" ", "_"), df.columns)
    return df


    # if len(df.columns) > 2:
    #     df = pd.concat((df, df['Predictive value (Type)'].str.split(" ", expand=True)), axis=1)\
    #         .rename(columns={0: "Predictive value", 1: "Type"})\
    #         .drop("Predictive value (Type)", axis=1)
    #     df["Type"] = df["Type"].str.strip(to_strip="()")
    #     df["prediction"] = df["Type"].map({"PPV": "AMP", "NPV": "non-AMP"}) \
    #         if "Human" not in strain \
    #         else df["Type"].map({"PPV": "non-AMP", "NPV": "AMP"})
    # if "Class" in df.columns and "Human erythrocytes" not in df["Strain Type"].values:
    #     df.drop(index=df.index[-1], axis=0, inplace=True)  # drop last row (DBAASP info boilerplate)
    #     df.rename({"Class": "prediction"}, axis="columns", inplace=True)
    # df["prediction_num"] = (df["prediction"] == "AMP").astype(int)
    # df.columns = map(lambda x: x.lower().replace(" ", "_"), df.columns)
    # return df


def clean_dbaasp_genome_preds(df: pd.DataFrame, strain: str) -> pd.DataFrame:
    df["prediction"] = df["Class"].map({"Active": "AMP", "Not Active": "non-AMP"})
    df.rename({"Predictive value": "score"}, axis="columns", inplace=True)
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


def clean_campr3_preds(df: pd.DataFrame) -> pd.DataFrame:
    print("Dropping Seq ID column...")
    df.drop("Seq. ID.", axis="columns", inplace=True)
    print("Columns to lowercase...")
    df.columns = df.columns.str.lower()
    print("Renaming columns...")
    df.rename({
        "class": "prediction",
        "amp probability": "score",
    }, axis="columns", inplace=True)
    print("Creating prediction_num...")
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


def generate_weights_grid(by: float = 0.01) -> np.ndarray:
    assert by <= 1
    xy = np.mgrid[0:1+by:by, 0:1+by:by]
    z = 1. - xy.sum(axis=0)
    return np.concatenate([xy[:, z >= 0.], np.atleast_2d(z[z >= 0.])]).T  # shape: (3, n)
