import numpy as np
from typing import Dict, Any
from modules.base import BaseAnalyzer
from modules.emotion.face_cropper import YOLOv8FaceCropper
from modules.emotion.vit_model import ViTEmotionClassifier
from modules.emotion.temporal_smoother import TemporalEmotionSmoother
from core.config import settings

class EmotionAnalyzer(BaseAnalyzer):
    """
    Unified Facial Emotion & Clinical Stress Analyzer.
    """

    def __init__(self):
        super().__init__(name="EmotionAnalyzer")
        self.face_cropper = YOLOv8FaceCropper(model_path=settings.FATIGUE_YOLO_PATH)
        self.classifier = ViTEmotionClassifier(model_path=settings.EMOTION_MODEL_PATH)
        self.smoother = TemporalEmotionSmoother(window_size=settings.EMOTION_TEMPORAL_WINDOW)

    def load_model(self) -> bool:
        cropper_ok = self.face_cropper.load()
        classifier_ok = self.classifier.load()
        self._is_loaded = cropper_ok and classifier_ok
        return self._is_loaded

    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        frame = data.get("frame")
        face_crop = None

        if frame is not None:
            face_crop = self.face_cropper.crop_face(frame)

        raw_result = self.classifier.predict_emotion(face_crop)
        smoothed_result = self.smoother.update(raw_result)
        smoothed_result["face_detected"] = face_crop is not None
        return smoothed_result
