import os

from Bio import SeqIO

from classif.stm.prediction import get_stm_predictions


def predict_stm(input_path: str, output_dir: str = "", verbose: bool = True) -> None:
    payload = "".join(item.format("fasta") for item in SeqIO.parse(input_path, "fasta"))
    result = get_stm_predictions(payload, verbose)
    outfile = os.path.basename(input_path).replace(".fasta", f"_pred_stm.csv")
    outfile = os.path.join(output_dir, outfile)
    if result is not None:
        result.to_csv(outfile, index=False)
    if verbose:
        print(f"saved predictions to {outfile}")
