import numpy as np
from pyquaternion import Quaternion

def format_time(seconds: float, is_showing_milliseconds: bool):
    days = int(seconds // (24 * 3600))
    seconds %= (24 * 3600)
    hours = int(seconds // 3600)
    seconds %= 3600
    minutes = int(seconds // 60)
    seconds %= 60

    formatted_time = ""
    if days > 0:
        formatted_time += f"{days}d "
    if hours > 0:
        formatted_time += f"{str(hours).zfill(2)}h "
    if minutes > 0:
        formatted_time += f"{str(minutes).zfill(2)}m "
    if is_showing_milliseconds:
        formatted_time += f"{seconds:6.3f}s"
    else:
        formatted_time += f"{seconds:2.0f}s"

    return formatted_time

def project_vector_a_onto_plane_b(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    # Projects vector A onto the plane represented by its normal vector B.
    # Assume B is a unit vector.
    return a - b * np.dot(a, b)

def project_a_onto_b(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    # Projects vector A onto vector B.
    return (np.dot(a, b) / np.linalg.norm(b)) * b

def vector_normalize(a: np.ndarray) -> np.ndarray:
    # Normalize vector A so that it is a unit vector.
    return a / np.linalg.norm(a)
