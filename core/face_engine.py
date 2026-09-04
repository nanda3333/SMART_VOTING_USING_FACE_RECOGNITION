import numpy as np
import cv2
from deepface import DeepFace

MODEL_NAME = "Facenet512"
DETECTOR_BACKEND = "opencv"
COSINE_THRESHOLD = 0.40

def generate_embedding(image_bytes: bytes) -> np.ndarray | None:
    np_img = np.frombuffer(image_bytes, np.uint8)
    frame = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

    try:
        results = DeepFace.represent(
            img_path=frame,
            model_name=MODEL_NAME,
            detector_backend=DETECTOR_BACKEND,
            enforce_detection=True,
            align=True
        )
        if len(results) > 0:
            return np.array(results[0]["embedding"], dtype=np.float32)
    except Exception:
        return None
    return None

def verify_voter_face(query_embedding: np.ndarray, registry: list[tuple[str, np.ndarray]]) -> tuple[str | None, float]:
    if not registry:
        return None, 1.0

    best_voter_hash = None
    min_distance = float("inf")

    query_norm = query_embedding / np.linalg.norm(query_embedding)

    for voter_hash, stored_embedding in registry:
        stored_norm = stored_embedding / np.linalg.norm(stored_embedding)
        cosine_distance = 1.0 - float(np.dot(query_norm, stored_norm))

        if cosine_distance < min_distance:
            min_distance = cosine_distance
            best_voter_hash = voter_hash

    if min_distance <= COSINE_THRESHOLD:
        return best_voter_hash, min_distance

    return None, min_distance