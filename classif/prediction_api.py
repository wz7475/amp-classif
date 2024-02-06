import os

import Bio
import pandas as pd

from classif import utils
from classif.config import Config
from classif.prediction_helpers import get_ampscanner_predictions, get_dbaasp_predictions, get_dbaasp_genome_predictions, \
    get_campr3_predictions, get_stm_predictions

"""
top level functions to make predictions with certain models/dbs
- ampscanner
- dbaaasp
- campr3
- stm
"""


def predict_ampscanner(input_path: str, output_dir: str, verbose: bool = True) -> None:
    basename = os.path.splitext(os.path.basename(input_path))[0]
    outfile = os.path.join(output_dir, f"{basename}_pred_ampscannerv2.csv")
    result = utils.clean_ampscanner_preds(get_ampscanner_predictions(input_path, verbose))
    result.to_csv(outfile, index=False)


def predict_dbaasp(input_path: str, output_dir: str, strain: str = "Escherichia coli ATCC 25922",
                   verbose: bool = True) -> None:
    payload = list(Bio.SeqIO.parse(input_path, "fasta"))
    if not strain:
        names = [item.id for item in payload]  # backup of actual sequence ids bc of a bug in dbaasp server-side code
        for i, item in enumerate(payload):
            item.id = str(i)
    payload = (item.format("fasta") for item in payload)
    result = (get_dbaasp_predictions("".join(chunk), strain, verbose)
              for chunk in utils.split_into_chunks(payload, chunk_size=Config.DBAASP_CHUNK_SIZE))
    result = pd.concat((partial for partial in result if partial is not None), axis="rows", ignore_index=True)
    basename = os.path.splitext(os.path.basename(input_path))[0]
    strain = strain.replace(' ', '_') if strain else "general"
    outfile = os.path.join(output_dir, f"{basename}_pred_dbaasp_{strain}.csv")
    if strain == "general":
        result["id"] = names
    if result is not None:
        result.to_csv(outfile, index=False)
    if verbose:
        print(f"saved predictions to {outfile}")


def predict_dbaasp_genome(input_path: str, output_dir: str = "",
                          strain: str = "", genbank_id: int = 2137, verbose: bool = True) -> None:
    payload = (item.format("fasta") for item in Bio.SeqIO.parse(input_path, "fasta"))
    result = (get_dbaasp_genome_predictions("".join(chunk), strain, genbank_id, verbose=verbose)
              for chunk in sorted(utils.split_into_chunks(payload, chunk_size=Config.DBAASP_GENOME_CHUNK_SIZE)))
    result = pd.concat((partial for partial in result if partial is not None), axis="rows", ignore_index=True)
    outfile = os.path.basename(input_path).replace(".fasta", f"_pred_dbaasp_genome_{strain.replace(' ', '_')}.csv")
    outfile = os.path.join(output_dir, outfile)
    if result is not None:
        result.to_csv(outfile, index=False)
    if verbose:
        print(f"saved predictions to {outfile}")


def predict_campr3(input_path: str, output_dir: str = "", verbose: bool = True) -> None:
    payload = "".join(item.format("fasta") for item in Bio.SeqIO.parse(input_path, "fasta"))
    result = get_campr3_predictions(payload, verbose)
    for algo, df in result.items():
        outfile = os.path.basename(input_path).replace(".fasta", f"_pred_{algo}.csv")
        outfile = os.path.join(output_dir, outfile)
        if df is not None:
            df.to_csv(outfile, index=False)
        if verbose:
            print(f"saved predictions to {outfile}")


def predict_stm(input_path: str, output_dir: str = "", verbose: bool = True) -> None:
    payload = "".join(item.format("fasta") for item in Bio.SeqIO.parse(input_path, "fasta"))
    result = get_stm_predictions(payload, verbose)
    outfile = os.path.basename(input_path).replace(".fasta", f"_pred_stm.csv")
    outfile = os.path.join(output_dir, outfile)
    if result is not None:
        result.to_csv(outfile, index=False)
    if verbose:
        print(f"saved predictions to {outfile}")

if __name__ == "__main__":
    # predict_stm('resources/TEST.fasta', 'data')
    # predict_campr3('resources/TEST.fasta', 'data')
    predict_ampscanner('resources/TEST.fasta', 'data')
    # predict_dbaasp('data/amp_high.fasta', 'data')
    # predict_dbaasp_genome('data/amp_high.fasta', 'data')
    # predict_campr3('data/amp_high.fasta', 'data')
    # predict_stm('data/amp_high.fasta', 'data')