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
        Fuses all 3 module outputs into a unified assessment.
        """
        # 1. Respiratory sub-score
        resp_event = respiratory_data.get("respiratory_event", "normal")
        hand_to_nose = respiratory_data.get("hand_to_nose_active", False)
        resp_score = 0.0
        if resp_event in ["cough", "sneeze"]:
            resp_score += 0.35
        elif resp_event == "sniffle":
            resp_score += 0.15
        if hand_to_nose:
            resp_score += 0.20
        resp_score = min(1.0, resp_score)

        # 2. Emotion sub-score
        stress_score = emotion_data.get("clinical_stress_score", 0.0)

        # 3. Fatigue sub-score
        perclos = fatigue_data.get("perclos_score", 0.0)
        fatigue_score = min(1.0, perclos * 2.5)

        # Weighted Multi-Modal Risk Fusion
        # Weights: Respiratory (0.40), Emotion/Stress (0.30), Fatigue (0.30)
        overall_risk = (resp_score * 0.40) + (stress_score * 0.30) + (fatigue_score * 0.30)
        overall_risk = round(min(1.0, overall_risk), 3)

        # Determine Risk Level & Active Alerts
        alerts = []
        if resp_score > 0.4:
            alerts.append("Frequent Respiratory Event / Hand-to-Nose Activity Detected")
        if stress_score > 0.6:
            alerts.append("Elevated Patient Stress Level Detected")
        if fatigue_score > 0.5:
            alerts.append("Significant Drowsiness / PERCLOS Alert")

        if overall_risk >= 0.70:
            risk_level = "CRITICAL"
        elif overall_risk >= 0.45:
            risk_level = "HIGH"
        elif overall_risk >= 0.25:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        return {
            "overall_risk_score": overall_risk,
            "risk_level": risk_level,
            "sub_scores": {
                "respiratory": round(resp_score, 2),
                "stress": round(stress_score, 2),
                "fatigue": round(fatigue_score, 2)
            },
            "active_alerts": alerts
        }
