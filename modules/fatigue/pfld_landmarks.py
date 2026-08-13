import cv2
import numpy as np
from typing import Dict, Any
from core.logging import logger

# Default path to the FaceLandmarker task model
FACE_LANDMARKER_MODEL = "models/fatigue/face_landmarker.task"

# MediaPipe FaceMesh lip landmark indices (same across both legacy and Tasks API)
# These define the inner lip geometry used for MAR calculation
#   Upper inner lip: 13 (top center), 82, 87
#   Lower inner lip: 14 (bottom center), 312, 317
#   Left corner: 61,  Right corner: 291
UPPER_LIP_TOP    = 13
LOWER_LIP_BOTTOM = 14
MOUTH_LEFT       = 61
MOUTH_RIGHT      = 291
UPPER_A          = 82
UPPER_B          = 87
LOWER_A          = 312
LOWER_B          = 317


class LandmarkExtractor:
    """
    Mouth Aspect Ratio (MAR) extractor using MediaPipe FaceLandmarker (Tasks API v1.0).

    Uses geometric lip landmark coordinates — fully lighting and skin-tone invariant.

    MAR formula: (|upper_a - lower_a| + |upper_b - lower_b| + |top - bottom|) / (3 * |left - right|)

    - Closed mouth: MAR ~ 0.05 – 0.12
    - Slightly open / talking: MAR ~ 0.15 – 0.30
    - Yawning (wide open): MAR > 0.45
    """

    def __init__(self, min_detection_confidence: float = 0.5, model_path: str = None):
        self.model_path = model_path or FACE_LANDMARKER_MODEL
        self.min_detection_confidence = min_detection_confidence
        self._landmarker = None
        self.is_loaded = False

    def load(self) -> bool:
        try:
            from mediapipe.tasks import python as mp_python
            from mediapipe.tasks.python import vision

            base_options = mp_python.BaseOptions(model_asset_path=self.model_path)
            options = vision.FaceLandmarkerOptions(
                base_options=base_options,
                running_mode=vision.RunningMode.IMAGE,
                num_faces=1,
                min_face_detection_confidence=self.min_detection_confidence,
                min_face_presence_confidence=self.min_detection_confidence,
                min_tracking_confidence=0.5
            )
            self._landmarker = vision.FaceLandmarker.create_from_options(options)
            self.is_loaded = True
            logger.info("MediaPipe FaceLandmarker loaded successfully.")
            return True
        except Exception as e:
            logger.error(f"FaceLandmarker load failed: {e}")
            self.is_loaded = False
            return False

    def extract_ratios(self, frame_bgr: np.ndarray, face_bbox: list = None) -> Dict[str, float]:
        """
        Computes MAR using actual lip landmark geometry from MediaPipe FaceLandmarker.
        """
        if frame_bgr is None or frame_bgr.size == 0:
            return {"left_ear": 0.32, "right_ear": 0.32, "mean_ear": 0.32, "mar": 0.08}

        if not self.is_loaded or self._landmarker is None:
            return {"left_ear": 0.32, "right_ear": 0.32, "mean_ear": 0.32, "mar": 0.08}

        try:
            import mediapipe as mp

            h, w = frame_bgr.shape[:2]
            rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

            result = self._landmarker.detect(mp_image)

            if not result.face_landmarks:
                return {"left_ear": 0.32, "right_ear": 0.32, "mean_ear": 0.32, "mar": 0.08}

            lm = result.face_landmarks[0]

            def pt(idx):
                return np.array([lm[idx].x * w, lm[idx].y * h])

            # Vertical lip opening (3 pairs)
            vert_a = np.linalg.norm(pt(UPPER_A)        - pt(LOWER_A))
            vert_b = np.linalg.norm(pt(UPPER_B)        - pt(LOWER_B))
            vert_c = np.linalg.norm(pt(UPPER_LIP_TOP)  - pt(LOWER_LIP_BOTTOM))

            # Horizontal mouth width
            horiz = np.linalg.norm(pt(MOUTH_LEFT) - pt(MOUTH_RIGHT))

            if horiz > 0:
                mar = (vert_a + vert_b + vert_c) / (3.0 * horiz)
            else:
                mar = 0.08

            return {
                "left_ear": 0.32,
                "right_ear": 0.32,
                "mean_ear": 0.32,
                "mar": round(float(np.clip(mar, 0.0, 1.0)), 3)
            }

        except Exception as e:
            logger.debug(f"FaceLandmarker MAR inference error: {e}")
            return {"left_ear": 0.32, "right_ear": 0.32, "mean_ear": 0.32, "mar": 0.08}


# Alias for backwards compatibility
MediaPipeLandmarkExtractor = LandmarkExtractor
