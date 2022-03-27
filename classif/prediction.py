import io
import os
import time

import Bio
import pandas as pd
import requests
from keras.models import load_model
from keras.preprocessing import sequence

from classif.config import Config
from classif import utils


def predict_ampscanner(input_path: str, output_dir: str, verbose: bool = True) -> None:
    basename = os.path.splitext(os.path.basename(input_path))[0]
    outfile = os.path.join(output_dir, f"{basename}_pred_ampscannerv2.csv")
    preds = utils.clean_ampscanner_preds(get_ampscanner_predictions(input_path, verbose))
    preds.to_csv(outfile, index=False)


def predict_dbaasp(input_path: str, strain: str = "Escherichia coli ATCC 25922", verbose: bool = True) -> None:
    with open(input_path, 'r') as f:
        payload = f.readlines()
    result = (get_dbaasp_predictions("".join(chunk), strain, verbose)
              for chunk in utils.split_into_chunks(payload, chunk_size=Config.DBAASP_CHUNK_SIZE))
    result = pd.concat((partial for partial in result if partial is not None), axis="rows", ignore_index=True)
    out = input_path.replace(".fasta", f"_pred_dbaasp_{strain.replace(' ', '_')}.csv")
    if result is not None:
        result.to_csv(out, index=False)
    if verbose:
        print(f"saved predictions to {out}")


def predict_campr3(input_path: str, verbose: bool = True) -> None:
    with open(input_path, 'r') as f:
        payload = f.readlines()
    # result = (get_dbaasp_predictions("".join(chunk), strain, verbose)
    #           for chunk in utils.split_into_chunks(payload, chunk_size=Config.DBAASP_CHUNK_SIZE))
    # result = pd.concat((partial for partial in result if partial is not None), axis="rows", ignore_index=True)
    # out = input_path.replace(".fasta", f"_pred_dbaasp_{strain.replace(' ', '_')}.csv")
    # if result is not None:
    #     result.to_csv(out, index=False)
    if verbose:
        print(f"saved predictions to {out}")


def predict_stm(input_path: str, verbose: bool = True) -> None:
    with open(input_path, 'r') as f:
        payload = "".join(f.readlines())
    result = get_stm_predictions(payload, verbose)
    out = input_path.replace(".fasta", f"_pred_stm.csv")
    if result is not None:
        result.to_csv(out, index=False)
    if verbose:
        print(f"saved predictions to {out}")


def get_ampscanner_predictions(input_path: str, verbose: bool = True) -> pd.DataFrame:
    os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
    if verbose:
        print("Encoding sequences...")
    X_test, warn, ids, seqs = utils.setup_ampscanner(input_path)
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


def get_dbaasp_predictions(payload: str, strain: str = "Escherichia coli ATCC 25922", verbose: bool = True) -> pd.DataFrame:
    if verbose:
        print("Sending prediction request to DBAASP...")
    response = requests.post(
        url=Config.DBAASP_URL,
        data={
            "strains": strain,
            "sequences": payload,
        })
    status, response = response.status_code, response.json()
    if verbose:
        print(f"request status: {status}")
    return utils.clean_dbaasp_preds(pd.DataFrame(response[1:], columns=response[0])) if status == 200 else None


def get_stm_predictions(payload: str, verbose: bool = True) -> pd.DataFrame:
    if verbose:
        print("Sending prediction request to STM...")
    response = requests.post(
        url=Config.STM_URL,
        data={
            "input": payload,
        })
    status, response = response.status_code, pd.read_html(response.text)[0]
    if verbose:
        print(f"request status: {status}")
    with io.StringIO(payload) as sequences:
        info = pd.DataFrame(
            ((s.id, str(s.seq)) for s in Bio.SeqIO.parse(sequences, "fasta")),
            columns=["id", "sequence"])
    response = pd.concat([info, response], axis="columns")
    return utils.clean_stm_preds(response) if status == 200 else None
