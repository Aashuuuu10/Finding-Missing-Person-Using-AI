import os
import PIL
import numpy as np
import streamlit as st
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision


# Path to the downloaded face_landmarker model
_MODEL_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", "resources", "face_landmarker.task"
)


def image_obj_to_numpy(image_obj) -> np.ndarray:
    """Convert a Streamlit-uploaded image object to a numpy array."""
    image = PIL.Image.open(image_obj)
    return np.array(image)


def extract_face_mesh_landmarks(image: np.ndarray):
    """
    Extract face mesh landmarks from an image using MediaPipe Tasks API.
    Returns a flattened list of all (x, y, z) landmarks if a face is found, else None.
    """
    base_options = mp_python.BaseOptions(model_asset_path=_MODEL_PATH)
    options = vision.FaceLandmarkerOptions(
        base_options=base_options,
        output_face_blendshapes=False,
        output_facial_transformation_matrixes=False,
        num_faces=1,
    )

    with vision.FaceLandmarker.create_from_options(options) as landmarker:
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image)
        result = landmarker.detect(mp_image)

        if result.face_landmarks:
            landmarks = result.face_landmarks[0]
            # Flatten all landmarks into a single list [x1, y1, z1, x2, y2, z2, ...]
            return [coord for lm in landmarks for coord in (lm.x, lm.y, lm.z)]
        else:
            st.error("Couldn't find face mesh in image. Please try another image.")
            return None
