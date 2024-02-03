import pandas as pd
import requests

from classif import config
from classif import utils


def predict_dbaasp(input_path: str, strain: str = "Escherichia coli ATCC 25922", verbose: bool = True) -> None:
    with open(input_path, 'r') as f:
        payload = "".join(f.readlines())
    if verbose:
        print("Sending prediction request to DBAASP...")
    """
    got 400 Bad request - API changed
    """
    response = requests.post(
        url=config.DBAASP_URL,
        data={
            "strains": strain,
            "sequences": payload,
        })
    status, response = response.status_code, response.json()
    out = input_path.replace(".fasta", f"_pred_dbaasp_{strain.replace(' ', '_')}.csv")
    df = utils.clean_dbaasp_preds(pd.DataFrame(response[1:], columns=response[0]))
    df.to_csv(out, index=False)
    if verbose:
        print(f"request status: {status}")
        print(f"saved predictions to {out}")


def predict_ampscanner(input_path: str, strain: str, verbose: bool = True) -> None:
    return None
