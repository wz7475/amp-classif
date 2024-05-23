""" module for inferencing all files with given suffix in input dir - saves results in same structure in output dir """

import argparse
import os
import pandas as pd

def process_file(filepath: str, output_filename: str):
    df = pd.read_csv(filepath, delimiter=",")
    df.rename(columns={"prediction": "Prediction"}, inplace=True)
    df.to_csv(output_filename, sep="\t", index=False)


def main(input_dir: str, suffix_to_process: str) -> None:
    # walk input dir
    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.endswith(suffix_to_process):
                filepath = os.path.join(root, file)
                process_file(filepath, filepath)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_dir', type=str, required=True)
    parser.add_argument('-s', '--suffix_to_process', type=str, required=True)
    args = parser.parse_args()
    main(args.input_dir, args.suffix_to_process)
    print('Done')
