import os
import time

import pandas as pd
from keras.engine.saving import load_model
from keras.preprocessing import sequence

import classif.ampscannerv2.utils
from classif.ampscannerv2.config import Config


def get_ampscanner_predictions(input_path: str, verbose: bool = True) -> pd.DataFrame:
    os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
    if verbose:
        print("Encoding sequences...")
    X_test, warn, ids, seqs = classif.ampscannerv2.utils.setup_ampscanner(input_path)
    X_test = sequence.pad_sequences(X_test, maxlen=Config.AMPSCANNER_MAX_LENGTH)

    if verbose:
        print("Loading model and weights from file: " + Config.AMPSCANNER_MODEL_PATH)
    model = load_model(Config.AMPSCANNER_MODEL_PATH)

    print("Making predictions...")
    preds = model.predict(X_test)
    rows = [
        [ids[i], f"AMP{warn[i]}" if pred[0] >= Config.AMPSCANNER_THRESHOLD else f"Non-AMP{warn[i]}", round(pred[0], 4), seqs[i]]
        for i, pred in enumerate(preds)
    ]
    if verbose:
        print("JOB FINISHED: " + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))
    return pd.DataFrame(rows, columns=["SeqID", "Prediction_Class", "Prediction_Probability", "Sequence"])
