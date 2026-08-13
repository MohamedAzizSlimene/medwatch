import numpy as np
import torch
from typing import Dict, Any, Optional
from core.logging import logger
from core.config import settings


# Comprehensive AudioSet label mapping for clinical respiratory sounds
AUDIOSET_TO_RESPIRATORY = {
    "Cough":                "cough",
    "Throat clearing":      "cough",
    "Sneeze":               "sneeze",
    "Sniff":                "sniffle",
    "Snort":                "sniffle",
    "Respiratory sounds":   "sniffle",
    "Wheeze":               "sniffle",
    "Snoring":              "sniffle",
    "Breathing":            "normal",
    "Burst, pop":           "cough",
}


class ASTRespiratoryClassifier:
    """
    Audio Spectrogram Transformer (AST) Respiratory Sound Classifier.
    Model: MIT/ast-finetuned-audioset-10-10-0.4593
    Detects: cough, sneeze, sniffle from 16kHz audio chunks.
    Threshold: 0.12 (12%) filters background silence while detecting real vocal/respiratory sounds.
    """

    CATEGORIES = ["normal", "cough", "sneeze", "sniffle"]
    CONFIDENCE_THRESHOLD = 0.12  # 12% minimum confidence threshold for audio detection

    def __init__(self, model_id: str = None):
        self.model_id = model_id or settings.RESPIRATORY_AST_MODEL_ID
        self.sample_rate = settings.RESPIRATORY_AUDIO_SAMPLE_RATE
        self.is_loaded = False
        self.model = None
        self.feature_extractor = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self._label_map: Dict[int, str] = {}

    def load(self) -> bool:
        try:
            from transformers import ASTForAudioClassification, ASTFeatureExtractor

            logger.info(f"Loading AST Respiratory model: {self.model_id}...")
            self.feature_extractor = ASTFeatureExtractor.from_pretrained(self.model_id)
            self.model = ASTForAudioClassification.from_pretrained(self.model_id)
            self.model.to(self.device)
            self.model.eval()

            self._label_map = {
                int(k): v
                for k, v in self.model.config.id2label.items()
            }

            self.is_loaded = True
            logger.info(f"AST Respiratory model loaded. {len(self._label_map)} AudioSet labels available.")
            return True

        except Exception as e:
            logger.error(f"Failed to load AST Respiratory model: {e}")
            return False

    def classify_audio_chunk(
        self,
        audio_data: np.ndarray,
        sample_rate: int = None
    ) -> Dict[str, Any]:
        if not self.is_loaded or audio_data is None or len(audio_data) == 0:
            return self._fallback_result()

        sr = sample_rate or self.sample_rate

        try:
            # 1. Energy gate: skip inference on silent background noise (< 0.01 RMS)
            rms = float(np.sqrt(np.mean(audio_data ** 2)))
            if rms < 0.008:
                return self._fallback_result()

            # 2. Peak normalization
            max_val = np.max(np.abs(audio_data))
            if max_val > 0.001:
                norm_audio = (audio_data / max_val).astype(np.float32)
            else:
                norm_audio = audio_data

            # 3. AST feature extraction and prediction
            inputs = self.feature_extractor(
                norm_audio,
                sampling_rate=sr,
                return_tensors="pt"
            ).to(self.device)

            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
                probs = torch.sigmoid(logits).squeeze().cpu().numpy()

            detected_event = "normal"
            best_confidence = 0.0

            for idx, prob in enumerate(probs):
                label = self._label_map.get(idx, "")
                category = AUDIOSET_TO_RESPIRATORY.get(label)
                if category and category != "normal" and float(prob) > self.CONFIDENCE_THRESHOLD:
                    if float(prob) > best_confidence:
                        best_confidence = float(prob)
                        detected_event = category

            category_scores: Dict[str, float] = {"normal": 1.0, "cough": 0.0, "sneeze": 0.0, "sniffle": 0.0}
            for idx, prob in enumerate(probs):
                label = self._label_map.get(idx, "")
                category = AUDIOSET_TO_RESPIRATORY.get(label)
                if category:
                    category_scores[category] = max(category_scores[category], float(prob))

            if detected_event != "normal":
                category_scores["normal"] = max(0.0, 1.0 - best_confidence)

            return {
                "detected_event": detected_event,
                "confidence": round(best_confidence if detected_event != "normal" else 1.0, 4),
                "probabilities": {k: round(v, 4) for k, v in category_scores.items()}
            }

        except Exception as e:
            logger.error(f"AST inference error: {e}")
            return self._fallback_result()

    def _fallback_result(self) -> Dict[str, Any]:
        return {
            "detected_event": "normal",
            "confidence": 0.0,
            "probabilities": {"normal": 1.0, "cough": 0.0, "sneeze": 0.0, "sniffle": 0.0}
        }
