import pandas as pd


def parse_happn_preds(input_file: str, verbose: bool = True) -> pd.DataFrame:
    if verbose:
        print(f"Parsing HAPPNN predictions from {input_file}...")
    assert(input_file.endswith("html"))
    df = pd.read_html(input_file)[0]
    df.drop(["#", "nTer", "cTer"], axis="columns", inplace=True)
    df.columns = df.columns.str.lower()
    df.rename({"prob": "score"}, axis="columns", inplace=True)
    df["prediction_num"] = (df["score"] > 0.5).astype(int)
    return df


def parse_hlppredfuse_preds(input_file: str, verbose: bool = True) -> pd.DataFrame:
    if verbose:
        print(f"Parsing HLPPred-Fuse predictions from {input_file}...")
    assert(input_file.endswith("html"))
    df = pd.read_html(input_file)[0]
    df.columns = df.iloc[0]
    df = df[1:]
    df.drop("S.NO", axis="columns", inplace=True)
    df.rename({
        "FASTA ID": "id",
        "HLP or Non-HLP": "prediction",
        "Prob": "score",
    }, axis="columns", inplace=True)
    df["prediction_num"] = df["prediction"].map({"HLP": 1, "Non-HLP": 0})
    df.columns = df.columns.str.lower()
    return df


def parse_hemopi_preds(input_file: str, verbose: bool = True) -> pd.DataFrame:
    if verbose:
        print(f"Parsing HLPPred-Fuse predictions from {input_file}...")
    assert(input_file.endswith("html"))
    df = pd.read_html(input_file)[0][:-1]
    df.columns = df.columns.droplevel()
    df.drop(['Unnamed: 8_level_1', 'Unnamed: 9_level_1', 'Unnamed: 10_level_1',
             'Unnamed: 11_level_1', 'Unnamed: 12_level_1', 'Unnamed: 13_level_1',
             'Unnamed: 14_level_1', 'Unnamed: 15_level_1', 'Unnamed: 16_level_1',
             'Unnamed: 17_level_1', 'Unnamed: 18_level_1', 'Unnamed: 19_level_1',
             'Unnamed: 20_level_1', 'Unnamed: 21_level_1', 'Unnamed: 22_level_1',
             'Unnamed: 23_level_1', 'Unnamed: 24_level_1', 'Unnamed: 25_level_1'],
            axis="columns", inplace=True)
    df.rename({
        "Peptide ID": "id",
        "Peptide Sequence": "sequence",
        "PROB Score": "score",
    }, axis="columns", inplace=True)
    df["score"] = df["score"].astype(float)
    df["prediction_num"] = (df["score"] >= 0.5).astype(int)
    return df


def clean_hemopred_preds(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = df.columns.str.lower()
    df["prediction_num"] = df["prediction"].map({"hemolytic": 1, "non-hemolytic": 0})
    df.rename({"protein": "id"}, axis="columns", inplace=True)
    return df

