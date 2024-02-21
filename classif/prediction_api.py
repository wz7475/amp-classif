import os

import Bio

from classif import utils
from classif.prediction_helpers import get_ampscanner_predictions, get_stm_predictions

"""
top level functions to make predictions with certain models/dbs
- ampscanner
- stm
"""


def predict_ampscanner(input_path: str, output_dir: str, verbose: bool = True) -> None:
    basename = os.path.splitext(os.path.basename(input_path))[0]
    outfile = os.path.join(output_dir, f"{basename}_pred_ampscannerv2.csv")
    result = utils.clean_ampscanner_preds(get_ampscanner_predictions(input_path, verbose))
    result.to_csv(outfile, index=False)


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
    predict_stm('resources/TEST.fasta', 'outputs')
    # predict_ampscanner('resources/TEST.fasta', 'outputs')
