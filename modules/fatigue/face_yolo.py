import os
import numpy as np
from typing import Dict, Any, Optional
from core.logging import logger


class YOLOv8FaceDetector:
    """
    YOLOv8 Face Detector Wrapper using Ultralytics.
    Detects faces in webcam frames and returns bounding boxes.
    Model: yolov8n-face.pt (nano, fast, suitable for real-time)
    """

    def __init__(self, model_path: str = "models/fatigue/yolov8n-face.pt"):
        self.model_path = model_path
        self.is_loaded = False
        self.model = None

    def load(self) -> bool:
        try:
            if not os.path.exists(self.model_path):
                logger.error(f"YOLOv8 weights not found at: {self.model_path}")
                return False

            from ultralytics import YOLO
            logger.info(f"Loading YOLOv8 Face model from {self.model_path}...")
            self.model = YOLO(self.model_path)
            self.is_loaded = True
            logger.info("YOLOv8 Face model loaded successfully.")
            return True

        except Exception as e:
            logger.error(f"Failed to load YOLOv8 Face model: {e}")
            return False

    def detect_face(self, frame: np.ndarray) -> Optional[Dict[str, Any]]:
        """
        Runs YOLOv8 face detection on a full BGR frame.
        Returns the largest detected face bounding box and confidence.
        Returns None if no face detected.
        """
        if not self.is_loaded or frame is None or frame.size == 0:
            return None

        try:
            # Run inference (verbose=False suppresses per-frame logs)
            results = self.model(frame, verbose=False)

            if not results or len(results) == 0:
                return None

            boxes = results[0].boxes
            if boxes is None or len(boxes) == 0:
                return None

            # Pick largest bounding box by area (most likely the patient's face)
            best_box = None
            best_area = 0

            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                area = (x2 - x1) * (y2 - y1)
                conf = float(box.conf[0].cpu().numpy())
                if area > best_area:
                    best_area = area
                    best_box = {
                        "bbox": [int(x1), int(y1), int(x2), int(y2)],
                        "confidence": round(conf, 4)
                    }

            return best_box

        except Exception as e:
            logger.error(f"YOLOv8 inference error: {e}")
            return None
