import datetime
import os
from collections import namedtuple
from typing import NamedTuple

import numpy as np
import pandas as pd
from sklearn import metrics
from tqdm import tqdm

from classif import config
from classif import utils

CONFIG = config.Config()


def benchmark(datasets_dir: str, predictions_dir: str, save_result: bool = True, verbose: bool = True) -> pd.DataFrame:
    result = None
    for model in tqdm(sorted(CONFIG.AVAILABLE_MODELS)):
        model_dir = os.path.join(predictions_dir, model)
        datasets = sorted([os.path.join(datasets_dir, fname)
                           for fname in os.listdir(datasets_dir)
                           if fname.endswith(".csv")])
        print(f"\nRunning benchmark for {model}...")

        full_ground_truth = np.empty((0,))
        full_predictions = np.empty((0,))

        for ground_truth, predictions_file in zip(datasets, sorted(os.listdir(model_dir))):
            predictions_file = os.path.join(model_dir, predictions_file)
            if verbose:
                print(f"Testing predictions in \n{predictions_file} \nagainst ground truth in \n{ground_truth}")

            y_pred = pd.read_csv(predictions_file)
            y_true = pd.read_csv(ground_truth)
            utils.ensure_consistency(y_pred, y_true)

            y_pred = y_pred["prediction_num"].to_numpy()
            y_true = y_true["active"].to_numpy()
            full_ground_truth = np.concatenate([full_ground_truth, y_true])
            full_predictions = np.concatenate([full_predictions, y_pred])

            partial_df = get_benchmark_df(y_true, y_pred, model, ground_truth.split("/")[-1])
            result = pd.concat((result, partial_df), axis="rows") if result is not None else partial_df

        model_summary = get_benchmark_df(full_ground_truth, full_predictions, model, dataset_name="OVERALL")
        result = pd.concat((result, model_summary), axis="rows")

    result = result.round(4)
    if save_result:
        result.to_csv(
            os.path.join(predictions_dir, f"benchmark_{datetime.datetime.now().strftime('%Y-%m-%d_%H:%M')}.csv"),
            index=False
        )
    return result


def get_benchmark_df(y_true: np.ndarray, y_pred: np.ndarray, model_name: str = "",
                     dataset_name: str = "") -> pd.DataFrame:
    m = calculate_metrics(y_true, y_pred)
    benchmark_df = pd.DataFrame({colname: [val] for colname, val in zip(m._fields, m)})
    benchmark_df[["model", "dataset"]] = [model_name, dataset_name]
    benchmark_df = benchmark_df.reindex(
        ["model", "dataset"] + [colname for colname in benchmark_df.columns
                                if colname not in {"model", "dataset"}],
        axis="columns"
    )
    return benchmark_df


def calculate_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> NamedTuple:
    # print(f"y_true: {y_true}, y_pred: {y_pred}")
    # print("Confusion matrix:")
    # print(metrics.confusion_matrix(y_true, y_pred))
    # print(metrics.confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel())
    tn, fp, fn, tp = metrics.confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    tpr = tp / (tp + fn) if (tp + fn) else np.nan
    tnr = tn / (tn + fp) if (tn + fp) else np.nan
    fpr = 1 - tnr  # np.nan propagates
    fnr = 1 - tpr  # np.nan propagates
    f1_score = metrics.f1_score(y_true, y_pred) if (tp + fp > 0 and tp + fn > 0) else np.nan
    accuracy = metrics.accuracy_score(y_true, y_pred)
    Metrics = namedtuple("Metrics", "tpr tnr fpr fnr f1_score accuracy")
    return Metrics._make((tpr, tnr, fpr, fnr, f1_score, accuracy))
