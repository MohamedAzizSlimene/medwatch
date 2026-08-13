import os
import cv2
import numpy as np
from typing import Dict, Any, Optional, Tuple
from core.logging import logger

HAND_LANDMARKER_MODEL = "models/respiratory/hand_landmarker.task"

# Key hand landmarks: 8 (index tip), 12 (middle tip), 4 (thumb tip), 0 (wrist)
HAND_TIPS = [8, 12, 4, 0, 5, 9]


class HandToNoseDetector:
    """
    Real AI Hand-to-Nose Gesture Detector using MediaPipe HandLandmarker Tasks API.

    Detects actual hand landmarks and checks if any finger tip or wrist enters
    the patient's face / nose bounding box.

    - Sitting normally (hands down): 0 hands near face → INACTIVE (False)
    - Bringing hand to nose/face: Finger landmarks enter face ROI → ACTIVE (True)
    - Lowering hand: Finger landmarks leave face ROI → INACTIVE (False)
    """

    def __init__(self, distance_threshold_pixels: float = 65.0, model_path: str = None):
        self.model_path = model_path or HAND_LANDMARKER_MODEL
        self.distance_threshold = distance_threshold_pixels
        self._landmarker = None
        self.is_loaded = False
        self.load()

    def load(self) -> bool:
        try:
            import mediapipe as mp
            from mediapipe.tasks import python as mp_python
            from mediapipe.tasks.python import vision

            if not os.path.exists(self.model_path):
                logger.warning(f"HandLandmarker task model not found at {self.model_path}")
                return False

            base_options = mp_python.BaseOptions(model_asset_path=self.model_path)
            options = vision.HandLandmarkerOptions(
                base_options=base_options,
                running_mode=vision.RunningMode.IMAGE,
                num_hands=2,
                min_hand_detection_confidence=0.4,
                min_hand_presence_confidence=0.4
            )
            self._landmarker = vision.HandLandmarker.create_from_options(options)
            self.is_loaded = True
            logger.info("MediaPipe HandLandmarker loaded successfully for gesture detection.")
            return True
        except Exception as e:
            logger.error(f"HandLandmarker load failed: {e}")
            self.is_loaded = False
            return False

    def detect_gesture_from_frame(
        self,
        frame_bgr: np.ndarray,
        face_bbox: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Detects if any hand landmarks enter the face/nose bounding box.
        """
        if frame_bgr is None or frame_bgr.size == 0 or face_bbox is None:
            return {"hand_to_nose_active": False, "confidence": 0.0}

        if not self.is_loaded or self._landmarker is None:
            return {"hand_to_nose_active": False, "confidence": 0.0}

        try:
            import mediapipe as mp

            h, w = frame_bgr.shape[:2]
            rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

            result = self._landmarker.detect(mp_image)

            if not result.hand_landmarks:
                return {"hand_to_nose_active": False, "confidence": 0.0}

            # Face bounding box with 25px margin around face
            fx1, fy1, fx2, fy2 = face_bbox
            margin = 25
            fx1_m = max(0, fx1 - margin)
            fy1_m = max(0, fy1 - margin)
            fx2_m = min(w, fx2 + margin)
            fy2_m = min(h, fy2 + margin)

            # Check if any finger tip or wrist falls inside face bounding box
            hand_near_face = False
            for hand_lm in result.hand_landmarks:
                for idx in HAND_TIPS:
                    pt_x = hand_lm[idx].x * w
                    pt_y = hand_lm[idx].y * h

                    if (fx1_m <= pt_x <= fx2_m) and (fy1_m <= pt_y <= fy2_m):
                        hand_near_face = True
                        break
                if hand_near_face:
                    break

            return {
                "hand_to_nose_active": bool(hand_near_face),
                "hands_detected": len(result.hand_landmarks),
                "confidence": 0.95 if hand_near_face else 0.05
            }

        except Exception as e:
            logger.debug(f"HandToNose gesture inference error: {e}")
            return {"hand_to_nose_active": False, "confidence": 0.0}

    def detect_gesture_from_coords(
        self,
        nose_coords: Optional[Tuple[int, int]],
        wrist_coords: Optional[Tuple[int, int]]
    ) -> Dict[str, Any]:
        if nose_coords is None or wrist_coords is None:
            return {"hand_to_nose_active": False, "confidence": 0.0}

        dist = np.sqrt((nose_coords[0] - wrist_coords[0])**2 + (nose_coords[1] - wrist_coords[1])**2)
        is_active = dist <= self.distance_threshold

        return {
            "hand_to_nose_active": bool(is_active),
            "distance": round(float(dist), 1),
            "confidence": 0.90 if is_active else 0.10
        }
