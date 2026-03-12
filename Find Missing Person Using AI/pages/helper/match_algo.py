import os
import pickle
import json
import traceback
import warnings
from collections import defaultdict

import pandas as pd
import numpy as np


warnings.filterwarnings(action="ignore")


from pages.helper import db_queries


def get_public_cases_data(status="NF"):
    try:
        result = db_queries.fetch_public_cases(train_data=True, status=status)
        d1 = pd.DataFrame(result, columns=["label", "face_mesh"])
        d1["face_mesh"] = d1["face_mesh"].apply(
            lambda x: json.loads(x) if isinstance(x, str) else x
        )
        # Drop rows where face_mesh is None or not a flat list of numbers
        d1 = d1[d1["face_mesh"].apply(
            lambda x: isinstance(x, list) and len(x) > 0 and not isinstance(x[0], list)
        )].copy()
        if len(d1) == 0:
            return pd.DataFrame(columns=["label"])
        d2 = pd.DataFrame(d1.pop("face_mesh").values.tolist(), index=d1.index).rename(
            columns=lambda x: "fm_{}".format(x + 1)
        )
        df = d1.join(d2)
        # Ensure all columns except label are float
        for col in df.columns:
            if col != "label":
                df[col] = pd.to_numeric(df[col], errors="coerce")
        df = df.dropna(subset=[c for c in df.columns if c != "label"])
        return df

    except Exception as e:
        traceback.print_exc()
        return None


def get_registered_cases_data(status="NF"):
    try:
        from pages.helper.db_queries import engine, RegisteredCases
        import pandas as pd
        import json
        from sqlmodel import Session, select

        with Session(engine) as session:
            result = session.exec(
                select(
                    RegisteredCases.id,
                    RegisteredCases.face_mesh,
                    RegisteredCases.status,
                )
            ).all()
            d1 = pd.DataFrame(result, columns=["label", "face_mesh", "status"])
            if status:
                d1 = d1[d1["status"] == status]
            d1["face_mesh"] = d1["face_mesh"].apply(
                lambda x: json.loads(x) if isinstance(x, str) else x
            )
            # Drop rows where face_mesh is None or not a flat list of numbers
            d1 = d1[d1["face_mesh"].apply(
                lambda x: isinstance(x, list) and len(x) > 0 and not isinstance(x[0], list)
            )].copy()
            if len(d1) == 0:
                return pd.DataFrame(columns=["label", "status"])
            d2 = pd.DataFrame(
                d1.pop("face_mesh").values.tolist(), index=d1.index
            ).rename(columns=lambda x: "fm_{}".format(x + 1))
            df = d1.join(d2)
            # Ensure all columns except label and status are float
            for col in df.columns:
                if col not in ["label", "status"]:
                    df[col] = pd.to_numeric(df[col], errors="coerce")
            df = df.dropna(subset=[c for c in df.columns if c not in ["label", "status"]])
            return df
    except Exception as e:
        traceback.print_exc()
        return None


from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import LabelEncoder


def match(distance_threshold=3):
    matched_images = defaultdict(list)
    match_scores = {}  # {reg_label: distance} for similarity score
    public_cases_df = get_public_cases_data()
    registered_cases_df = get_registered_cases_data()

    if public_cases_df is None or registered_cases_df is None:
        return {"status": False, "message": "Couldn't connect to database"}
    if len(public_cases_df) == 0 or len(registered_cases_df) == 0:
        return {"status": False, "message": "No public or registered cases found"}

    # Store original labels before encoding
    registered_cases_df = registered_cases_df.reset_index(drop=True)
    original_reg_labels = registered_cases_df.iloc[:, 0].tolist()

    # Reset index on public_cases_df so iterrows() gives sequential indices
    public_cases_df = public_cases_df.reset_index(drop=True)
    original_pub_labels = public_cases_df.iloc[:, 0].tolist()

    # Prepare training data - use index positions as labels for the classifier
    reg_features = registered_cases_df.iloc[:, 2:].values.astype(float)

    # Drop rows with NaN in registered features
    valid_reg_mask = ~np.isnan(reg_features).any(axis=1)
    reg_features = reg_features[valid_reg_mask]
    original_reg_labels = [l for l, v in zip(original_reg_labels, valid_reg_mask) if v]

    if len(reg_features) == 0:
        return {"status": False, "message": "No valid registered cases with face data"}

    # Create simple numeric labels for KNN (0, 1, 2, ...)
    numeric_labels = list(range(len(reg_features)))

    # Train KNN classifier with numeric labels
    knn = KNeighborsClassifier(n_neighbors=1, algorithm="ball_tree", weights="distance")
    knn.fit(reg_features, numeric_labels)

    # For each public submission, find the closest registered case
    for i, row in public_cases_df.iterrows():
        pub_label = original_pub_labels[i]  # Original public case ID
        face_encoding = np.array(row[1:]).astype(float)

        # Skip public cases with NaN face data
        if np.isnan(face_encoding).any():
            print(f"Skipping public case {pub_label}: contains NaN values")
            continue

        try:
            # Get distances to nearest neighbors
            closest_distances = knn.kneighbors([face_encoding])[0][0]
            closest_distance = np.min(closest_distances)
            print(f"Distance for case {pub_label}: {closest_distance}")

            # Lower distance = better match. Accept if below threshold.
            if closest_distance <= distance_threshold:
                # Get the index of the predicted registered case
                predicted_idx = knn.predict([face_encoding])[0]
                # Get the original UUID of the registered case
                reg_label = original_reg_labels[predicted_idx]
                # Store the match
                matched_images[reg_label].append(pub_label)
                # Store best (lowest) distance for this registered case
                if reg_label not in match_scores or closest_distance < match_scores[reg_label]:
                    match_scores[reg_label] = float(closest_distance)
        except Exception as e:
            print(f"Error processing public case {pub_label}: {str(e)}")
            continue

    # Convert distances to similarity percentages (0-100%)
    # Using exponential decay: score = 100 * exp(-distance)
    import math
    similarity_scores = {}
    for reg_label, dist in match_scores.items():
        # Clamp to reasonable range; distance 0 = 100%, distance >= threshold ≈ low %
        score = round(100.0 * math.exp(-dist * 0.7), 1)
        score = max(1.0, min(100.0, score))
        similarity_scores[reg_label] = score

    return {"status": True, "result": matched_images, "scores": similarity_scores}


if __name__ == "__main__":
    result = match()
    print(result)
