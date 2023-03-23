import datetime
import itertools
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


def benchmark(datasets_dir: str, predictions_dir: str, mode: str = "amp", save_result: bool = True,
              verbose: bool = True) -> pd.DataFrame:
    assert mode in ("amp", "toxicity")
    available_models = CONFIG.AVAILABLE_MODELS if mode == "amp" else CONFIG.TOXICITY_MODELS
    result = None
    for model in tqdm(sorted(available_models)):
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


def grid_search_weights(training_set: pd.DataFrame, grid_scale: float = 0.01, mode: str = "unit_sum",
                        top_k: int = 100, verbose: bool = True) -> pd.DataFrame:
    assert 0. < grid_scale < 1.
    assert mode in ("unit_sum", "full_cube")
    if verbose:
        print(f"Generating grid of weights; grid resolution: {grid_scale}")
    grid = utils.generate_weights_grid(by=grid_scale) if mode == "unit_sum" \
        else np.array(list(itertools.combinations(np.arange(0., 1+grid_scale, grid_scale), 3)))
    scores = dict()
    if verbose:
        print("Running grid search...")
    for i, weights in enumerate(tqdm(grid)):
        training_set["score"] = (
                training_set[[f"{name}_score" for name in CONFIG.MODELS_FOR_CANDIDATE_SELECTION]] * weights).sum(axis=1)
        eval_score = top_k_fraction_of_ones(training_set, k=top_k)
        scores[i] = (weights, eval_score)
    return pd.DataFrame([t for _, t in scores.items()],
                        columns=["weights", "metric"]).sort_values(by="metric", ascending=False)


def top_k_fraction_of_ones(predictions: pd.DataFrame, k: int = 100) -> float:
    ranked = predictions.sort_values(by="score", ascending=False)
    return ranked["class"][:k].sum() / k
