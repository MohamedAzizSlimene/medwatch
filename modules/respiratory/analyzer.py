import time
from typing import Dict, Any
from modules.base import BaseAnalyzer
from modules.respiratory.audio_classifier import ASTRespiratoryClassifier
from modules.respiratory.hand_to_nose_detector import HandToNoseDetector
from core.config import settings

class RespiratoryAnalyzer(BaseAnalyzer):
    """
    Unified Respiratory Health Monitoring Analyzer.
    Fuses audio classification (coughing, sneezing, sniffling using AST) with visual gesture detection (hand-to-nose activity).
    Uses strict state transition tracking (False -> True) so hand-to-nose gestures ONLY count on new hand touches.
    """

    def __init__(self):
        super().__init__(name="RespiratoryAnalyzer")
        self.audio_classifier = ASTRespiratoryClassifier(model_id=settings.RESPIRATORY_AST_MODEL_ID)
        self.hand_to_nose_detector = HandToNoseDetector()
        
        self.cough_count = 0
        self.sneeze_count = 0
        self.sniffle_count = 0
        self.hand_to_nose_count = 0
        
        self.last_cough_time = 0.0
        self.last_sneeze_time = 0.0
        self.last_sniffle_time = 0.0
        
        # State tracking to ensure 1 gesture = 1 count (no auto-incrementing)
        self.was_hand_to_nose_active = False

    def load_model(self) -> bool:
        self._is_loaded = self.audio_classifier.load()
        return self._is_loaded

    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        audio_result = {"detected_event": "normal", "confidence": 1.0}
        gesture_result = {"hand_to_nose_active": False, "confidence": 0.0}
        now = time.time()

        # 1. Process Audio Chunk if present
        if "audio_chunk" in data and data["audio_chunk"] is not None:
            audio_result = self.audio_classifier.classify_audio_chunk(data["audio_chunk"])
            event = audio_result.get("detected_event")
            conf = audio_result.get("confidence", 0.0)

            # Refractory debouncing for audio counters
            if event == "cough" and conf >= 0.20:
                if (now - self.last_cough_time) > 1.5:
                    self.cough_count += 1
                    self.last_cough_time = now
            elif event == "sneeze" and conf >= 0.15:
                if (now - self.last_sneeze_time) > 1.5:
                    self.sneeze_count += 1
                    self.last_sneeze_time = now
            elif event == "sniffle" and conf >= 0.20:
                if (now - self.last_sniffle_time) > 1.5:
                    self.sniffle_count += 1
                    self.last_sniffle_time = now

        # 2. Process Visual Hand-to-Nose Gesture
        nose_coords = data.get("nose_coords")
        wrist_coords = data.get("wrist_coords")
        frame = data.get("frame")
        face_bbox = data.get("face_bbox")

        if nose_coords and wrist_coords:
            gesture_result = self.hand_to_nose_detector.detect_gesture_from_coords(nose_coords, wrist_coords)
        elif frame is not None and face_bbox is not None:
            gesture_result = self.hand_to_nose_detector.detect_gesture_from_frame(frame, face_bbox)

        is_active = bool(gesture_result.get("hand_to_nose_active", False))

        # Strict State Transition: Count ONLY when transitioning from False -> True
        if is_active and not self.was_hand_to_nose_active:
            self.hand_to_nose_count += 1
            self.was_hand_to_nose_active = True
        elif not is_active:
            self.was_hand_to_nose_active = False

        return {
            "respiratory_event": audio_result.get("detected_event", "normal"),
            "audio_confidence": audio_result.get("confidence", 0.0),
            "hand_to_nose_active": is_active,
            "hand_to_nose_count": self.hand_to_nose_count,
            "cumulative_counts": {
                "cough": self.cough_count,
                "sneeze": self.sneeze_count,
                "sniffle": self.sniffle_count,
                "hand_to_nose": self.hand_to_nose_count
            }
        }
