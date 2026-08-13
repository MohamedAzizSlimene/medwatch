import numpy as np
from typing import Dict, Any
from modules.base import BaseAnalyzer
from modules.fatigue.face_yolo import YOLOv8FaceDetector
from modules.fatigue.pfld_landmarks import LandmarkExtractor
from modules.fatigue.perclos_calculator import PERCLOSCalculator
from core.config import settings
from core.logging import logger


class FatigueAnalyzer(BaseAnalyzer):
    """
    Unified Fatigue & Drowsiness Analyzer.
    Runs YOLOv8 face detector ONCE per frame and shares face_bbox.
    """

    def __init__(self):
        super().__init__(name="FatigueAnalyzer")
        self.face_detector = YOLOv8FaceDetector(model_path=settings.FATIGUE_YOLO_PATH)
        self.landmark_extractor = LandmarkExtractor(
            min_detection_confidence=settings.FACE_DETECTION_CONFIDENCE,
            model_path=settings.FATIGUE_FACE_LANDMARKER_PATH
        )
        self.perclos_calc = PERCLOSCalculator(
            window_seconds=settings.PERCLOS_WINDOW_SECONDS
        )

    def load_model(self) -> bool:
        yolo_ok = self.face_detector.load()
        mesh_ok = self.landmark_extractor.load()
        self._is_loaded = yolo_ok and mesh_ok
        return self._is_loaded

    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        frame = data.get("frame")

        if frame is None or frame.size == 0:
            return {
                "face_detected": False,
                "face_bbox": None,
                "perclos_score": 0.0,
                "status": "No Frame",
                "yawn_count": self.perclos_calc.yawn_count,
                "ear": 0.0,
                "mar": 0.0
            }

        # Step 1: Detect face with YOLOv8 (Single pass)
        face_info = self.face_detector.detect_face(frame)

        if face_info is None:
            return {
                "face_detected": False,
                "face_bbox": None,
                "perclos_score": round(
                    self.perclos_calc.add_reading(mean_ear=0.30, mar=0.15).get("perclos_score", 0.0), 4
                ),
                "status": "No Face Detected",
                "yawn_count": self.perclos_calc.yawn_count,
                "ear": 0.0,
                "mar": 0.0
            }

        # Step 2: Extract EAR & MAR from face crop
        bbox = face_info.get("bbox")
        ratios = self.landmark_extractor.extract_ratios(frame, face_bbox=bbox)
        mean_ear = ratios.get("mean_ear", 0.30)
        mar = ratios.get("mar", 0.15)

        # Step 3: Update PERCLOS rolling window
        fatigue_metrics = self.perclos_calc.add_reading(mean_ear=mean_ear, mar=mar)
        fatigue_metrics["face_detected"] = True
        fatigue_metrics["face_bbox"] = bbox
        fatigue_metrics["ear"] = round(mean_ear, 3)
        fatigue_metrics["mar"] = round(mar, 3)
        fatigue_metrics["yolo_confidence"] = face_info.get("confidence", 0.0)

        return fatigue_metrics
