import os

import classif.ampscannerv2.utils
from classif.ampscannerv2.prediction import get_ampscanner_predictions


def predict_ampscanner(input_path: str, output_dir: str, verbose: bool = True) -> None:
    basename = os.path.splitext(os.path.basename(input_path))[0]
    outfile = os.path.join(output_dir, f"{basename}_pred_ampscannerv2.csv")
    result = classif.ampscannerv2.utils.clean_ampscanner_preds(get_ampscanner_predictions(input_path, verbose))
    result.to_csv(outfile, index=False)
