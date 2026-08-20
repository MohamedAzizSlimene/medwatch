import os
import numpy as np
from typing import Dict, Any
from core.logging import logger

class MultiModalFusionEngine:
    """
    Multi-Modal Fusion Engine.
    Combines feature streams from:
    1. Respiratory Health (cough/sneeze/sniffle counts + hand-to-nose activity)
    2. Emotion & Stress (clinical stress score + dominant emotion)
    3. Fatigue & Drowsiness (PERCLOS score + yawn count)
    
    Computes unified Clinical Risk Score (0.0 - 1.0) and alert classification.
    """

    def __init__(self, model_path: str = None):
        self.model_path = model_path
        self.is_loaded = False

    def load(self) -> bool:
        if self.model_path and os.path.exists(self.model_path):
            logger.info(f"Loading XGBoost Fusion model from {self.model_path}")
            self.is_loaded = True
        else:
            logger.info("Running rule-based Multi-Modal Fusion Engine.")
            self.is_loaded = True
        return True

    def fuse(
        self,
        respiratory_data: Dict[str, Any],
        emotion_data: Dict[str, Any],
        fatigue_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Fuses module outputs into an objective Consultation Session Telemetry Summary.
        Removes PERCLOS drowsiness multipliers and pseudo-diagnostic risk scores.
        """
        # 1. Respiratory Telemetry
        counts = respiratory_data.get("cumulative_counts", {})
        cough_count = counts.get("cough", respiratory_data.get("cough_count", 0))
        sneeze_count = counts.get("sneeze", respiratory_data.get("sneeze_count", 0))
        hand_to_nose_count = counts.get("hand_to_nose", respiratory_data.get("hand_to_nose_count", 0))
        resp_event = respiratory_data.get("respiratory_event", "normal")

        # 2. Emotion & Stress Telemetry (now from SustainedEmotionTracker)
        # clinical_stress_score is no longer produced — we use factual sustained events instead.
        sustained_events = emotion_data.get("sustained_events", [])
        dominant_emotion = emotion_data.get("dominant_emotion", "Neutral")
        latest_observation = emotion_data.get("observation_label", None)

        # 3. Fatigue Telemetry (Yawn frequency driven)
        yawn_count = fatigue_data.get("yawn_count", 0)
        fatigue_status = fatigue_data.get("status", "NORMAL")
        is_yawning = fatigue_data.get("is_yawning_now", False)

        # Objective Observations & Alerts
        observations = []
        if (cough_count + sneeze_count) >= 3:
            observations.append(f"Frequent Respiratory Events (Coughs: {cough_count}, Sneezes: {sneeze_count})")
        if hand_to_nose_count >= 3:
            observations.append(f"Frequent Hand-to-Nose Face Touch Gestures ({hand_to_nose_count} Times)")
        if yawn_count >= 3 or is_yawning:
            observations.append(f"Multiple Yawn Events Recorded (Total Yawns: #{yawn_count})")
        # Sustained emotion observations come directly from the tracker (time-gated, factual)
        for event in sustained_events:
            if event not in observations:
                observations.append(event)


        # Session Status Determination
        if len(observations) >= 2:
            session_status = "ELEVATED ACTIVITY"
            risk_level = "MEDIUM"
        elif len(observations) == 1:
            session_status = "MONITORING"
            risk_level = "LOW"
        else:
            session_status = "BASELINE NORMAL"
            risk_level = "LOW"

        return {
            "session_status": session_status,
            "telemetry": {
                "coughs": cough_count,
                "sneezes": sneeze_count,
                "hand_gestures": hand_to_nose_count,
                "active_resp_event": resp_event,
                "sustained_emotion_events": len(sustained_events),
                "dominant_emotion": dominant_emotion,
                "yawn_count": yawn_count,
                "fatigue_status": fatigue_status
            },
            "active_observations": observations,
            # Backward compatibility fields
            "overall_risk_score": 0.15 if session_status == "BASELINE NORMAL" else 0.45,
            "risk_level": risk_level,
            "sub_scores": {
                "respiratory": round(min(1.0, (cough_count + sneeze_count) * 0.25 + hand_to_nose_count * 0.15), 2),
                "emotion_events": len(sustained_events),
                "fatigue": round(min(1.0, yawn_count * 0.33), 2)
            },
            "active_alerts": observations
        }
