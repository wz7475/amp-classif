from typing import Tuple
import os
import pandas as pd


def get_confusion_matrix(df_positives: pd.DataFrame, df_negatives: pd.DataFrame, pred_col_name: str,
                         postives_value: str, negatives_value: str) -> \
        Tuple[int, int, int, int, int]:
    all_actual_positives = len(df_positives)
    all_actual_negatives = len(df_negatives)

    true_positives = len(df_positives[df_positives[pred_col_name] == postives_value])
    false_negatives = len(df_positives[df_positives[pred_col_name] == negatives_value])

    false_positives = len(df_negatives[df_negatives[pred_col_name] == postives_value])
    true_negatives = len(df_negatives[df_negatives[pred_col_name] == negatives_value])

    failed_num = all_actual_positives + all_actual_negatives - (
            true_negatives + false_negatives + false_negatives + true_positives)

    return true_negatives, false_positives, false_negatives, true_positives, failed_num


def get_metrics(tn, fp, fn, tp):
    acc = (tp + tn) / (tn + fp + fn + tp)
    tpr = tp / (tp + fn)
    fpr = fp / (tn + fp)
    return acc, fpr, tpr


def analyze_experiment(positives_path, negatives_path, results_container: list, verbose=True):
    df_positives = pd.read_csv(positives_path, delimiter="\t")
    df_negatives = pd.read_csv(negatives_path, delimiter="\t")

    tn, fp, fn, tp, err = get_confusion_matrix(df_positives, df_negatives, "Prediction", "AMP", "non-AMP")

    acc, fpr, tpr = get_metrics(tn, fp, fn, tp)
    results_container.append([tn, fp, fn, tp, acc, fpr, tpr])
    if verbose:
        print(f"tn: {tn}, fp: {fp}, fn: {fn}, tp: {tp}, err: {err}")
        print(f"acc {acc}, fpr {fpr} tpr {tpr}")


def get_outputs_pairs(output_dir: str):
    allowed_suffixes = ["active_32.tsv", "inactive_128.tsv"]

    # get all paths
    all_paths_for_pairs = set()
    for root, _, files in os.walk(output_dir):
        for file in files:
            fullpath = os.path.join(root, file)
            for allowed_suf in allowed_suffixes:
                if fullpath.endswith(allowed_suf):
                    all_paths_for_pairs.add(fullpath)

    # get pairs
    pairs = []
    already_added_as_complementary = []
    for current_path in all_paths_for_pairs:
        if current_path in already_added_as_complementary:
            continue
        if current_path.endswith(allowed_suffixes[0]):
            base = current_path.split(allowed_suffixes[0])[0]
            complementary_path = f"{base}{allowed_suffixes[1]}"
        else:
            base = current_path.split(allowed_suffixes[1])[0]
            complementary_path = f"{base}{allowed_suffixes[0]}"
        pairs.append(sorted((current_path, complementary_path)))
        already_added_as_complementary.append(complementary_path)
    return pairs


if __name__ == "__main__":
    results_container = []
    pairs = get_outputs_pairs("all_out")
    for r in pairs:
        analyze_experiment(*r, results_container, verbose=False)
        results_container[-1].insert(0, r[0].split("active_32")[0])
    print(results_container)

    results_df = pd.DataFrame(results_container, columns=["name", "tn", "fp", "fn", "tp", "acc", "fpr", "tpr"])
    results_df.to_csv(os.path.join("all_out", "tasks_1_2.tsv"), sep="\t", index=False)