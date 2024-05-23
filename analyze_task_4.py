""" script for

Are AMP classifiers able to capture the difference between peptides which are syntactically similar but exhibit varied activity?

- records are paired (row 1-2, 3-4, 5-6 ...) - each pair:  first active, second inactive
"""
from argparse import ArgumentParser

import pandas as pd


def main(input_file: str):
    df = pd.read_csv(input_file, delimiter="\t")
    correctly_predicted_pairs = 0
    all_pairs = 0
    for i, g in df.groupby(df.index // 2):
        all_pairs += 1
        if g["Prediction"].iloc[0] == "AMP" and g["Prediction"].iloc[1] == "non-AMP":
            correctly_predicted_pairs += 1
    return correctly_predicted_pairs, all_pairs


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("output")
    args = parser.parse_args()

    print(args)
    correctly_predicted, all_pairs = main(args.input)
    print(correctly_predicted, all_pairs)
    results_df = pd.DataFrame({"distinguished": [correctly_predicted], "all": [all_pairs]})
    results_df.to_csv(args.output, sep="\t", index=False)