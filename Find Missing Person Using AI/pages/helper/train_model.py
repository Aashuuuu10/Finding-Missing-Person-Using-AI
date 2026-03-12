import os
import json
import pickle
import traceback

import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.neighbors import KNeighborsClassifier

from pages.helper import db_queries


def get_train_data(submitted_by: str):
    """
    Gets the training data for the user logged in

    Args:
        submitted_by: str
    """

    try:
        result = db_queries.get_training_data(submitted_by)

        d1 = pd.DataFrame(result, columns=["label", "face_mesh"])

        # Parse JSON face_mesh strings and filter out null/invalid entries
        d1["face_mesh"] = d1["face_mesh"].apply(
            lambda x: json.loads(x) if isinstance(x, str) else x
        )
        # Drop rows where face_mesh is None or not a flat list of numbers
        d1 = d1[d1["face_mesh"].apply(
            lambda x: isinstance(x, list) and len(x) > 0 and not isinstance(x[0], list)
        )].copy()

        if len(d1) == 0:
            return pd.Series(dtype=str), pd.DataFrame()

        d2 = pd.DataFrame(d1.pop("face_mesh").values.tolist(), index=d1.index).rename(
            columns=lambda x: "fm_{}".format(x + 1)
        )
        df = d1.join(d2)

        # Ensure all feature columns are numeric, drop rows with any NaN
        feature_cols = [c for c in df.columns if c != "label"]
        for col in feature_cols:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        df = df.dropna(subset=feature_cols)

        return df["label"], df.drop("label", axis=1)

    except Exception as e:
        traceback.print_exc()
        raise e


def train(submitted_by: str):
    """
    Trains a KNN Model on the submitted cases.

    Args:
        submitted_by: str

    Returns:
        dict - {
            "status": bool - whether the functional call was successful or not
            "message": str - message returned on each case
        }

    """
    model_name = "classifier.pkl"
    if os.path.isfile(model_name):
        os.remove(model_name)
    try:
        labels, key_pts = get_train_data(submitted_by)
        if len(labels) == 0:
            return {"status": False, "message": "No cases submmited by this user"}
        le = LabelEncoder()
        encoded_labels = le.fit_transform(labels)
        # Ensure key_pts is a proper 2D float array
        import numpy as np
        key_pts_array = np.array(key_pts, dtype=float)
        classifier = KNeighborsClassifier(
            n_neighbors=len(labels), algorithm="ball_tree", weights="distance"
        )
        classifier.fit(key_pts_array, encoded_labels)

        with open(model_name, "wb") as file:
            pickle.dump((le, classifier), file)
        return {"status": True, "message": "Model Refreshed"}
    except Exception as e:
        traceback.print_exc()
        return {"status": False, "message": str(e)}


if __name__ == "__main__":
    result = train("admin")
