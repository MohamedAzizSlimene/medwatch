import cv2
import numpy as np
from typing import Optional
from modules.fatigue.face_yolo import YOLOv8FaceDetector
from core.config import settings
from core.logging import logger


class YOLOv8FaceCropper:
    """
    Detects face ROI in a full webcam frame using YOLOv8 Face Detector
    and crops a square (1:1 aspect ratio) face ROI for ViT emotion classification.
    Square aspect ratio preserves natural facial proportions without distortion.
    """

    def __init__(self, model_path: str = None):
        self.detector = YOLOv8FaceDetector(model_path=model_path or settings.FATIGUE_YOLO_PATH)

    def load(self) -> bool:
        return self.detector.load()

    def crop_face(
        self,
        frame_bgr: np.ndarray,
        padding_pct: float = 0.20
    ) -> Optional[np.ndarray]:
        """
        Detects primary face in a BGR frame and returns a square cropped face image (RGB numpy array).
        Returns None if no face is detected.
        """
        if frame_bgr is None or frame_bgr.size == 0:
            return None

        face_info = self.detector.detect_face(frame_bgr)
        if not face_info or "bbox" not in face_info:
            return None

        x1, y1, x2, y2 = face_info["bbox"]
        h, w = frame_bgr.shape[:2]

        bw = x2 - x1
        bh = y2 - y1
        center_x = x1 + bw // 2
        center_y = y1 + bh // 2

        # Make crop square based on max dimension + padding
        max_dim = max(bw, bh)
        side = int(max_dim * (1.0 + padding_pct))

        crop_x1 = max(0, center_x - side // 2)
        crop_y1 = max(0, center_y - side // 2)
        crop_x2 = min(w, center_x + side // 2)
        crop_y2 = min(h, center_y + side // 2)

        if crop_x2 <= crop_x1 or crop_y2 <= crop_y1:
            return None

        face_crop_bgr = frame_bgr[crop_y1:crop_y2, crop_x1:crop_x2]
        face_crop_rgb = cv2.cvtColor(face_crop_bgr, cv2.COLOR_BGR2RGB)
        return face_crop_rgb
