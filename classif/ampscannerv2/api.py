import os

import classif.ampscannerv2.utils
from classif.ampscannerv2.prediction import get_ampscanner_predictions


def predict_ampscanner(input_path: str, output_pth: str, verbose: bool = True) -> None:
    result = classif.ampscannerv2.utils.clean_ampscanner_preds(get_ampscanner_predictions(input_path, verbose))
    result.to_csv(output_pth, index=False)