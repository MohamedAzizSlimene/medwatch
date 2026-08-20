import numpy as np
from typing import Dict, Any
from modules.base import BaseAnalyzer
from modules.emotion.face_cropper import YOLOv8FaceCropper
from modules.emotion.vit_model import ViTEmotionClassifier
from modules.emotion.temporal_smoother import SustainedEmotionTracker
from core.config import settings

class EmotionAnalyzer(BaseAnalyzer):
    """
    Unified Facial Emotion Analyzer with Sustained Expression Tracking.
    Replaces the old TemporalEmotionSmoother (2-frame 70/30 + ×1.2 stress amplifier)
    with a 30-frame rolling mean and a 3-second sustain gate.
    Output includes sustained_events and observation_label instead of clinical_stress_score.
    """

    def __init__(self):
        super().__init__(name="EmotionAnalyzer")
        self.face_cropper = YOLOv8FaceCropper(model_path=settings.FATIGUE_YOLO_PATH)
        self.classifier = ViTEmotionClassifier(model_path=settings.EMOTION_MODEL_PATH)
        self.tracker = SustainedEmotionTracker()

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
        tracked_result = self.tracker.update(raw_result)
        tracked_result["face_detected"] = face_crop is not None
        return tracked_result

