import numpy as np
import torch
from typing import Dict, Any, Optional
from core.logging import logger
from core.config import settings


# Comprehensive AudioSet label mapping for clinical respiratory sounds
AUDIOSET_TO_RESPIRATORY = {
    "Cough":                "cough",
    "Throat clearing":      "cough",
    "Burst, pop":           "cough",
    "Sneeze":               "sneeze",
    "Snort":                "sneeze",
    "Gasp":                 "sneeze",
    "Pant":                 "sneeze",
    "Snicker":              "sneeze",
    "Sniff":                "sniffle",
    "Respiratory sounds":   "sniffle",
    "Wheeze":               "sniffle",
    "Snoring":              "sniffle",
    "Breathing":            "normal",
}


class ASTRespiratoryClassifier:
    """
    Audio Spectrogram Transformer (AST) Respiratory Sound Classifier.
    Model: MIT/ast-finetuned-audioset-10-10-0.4593
    Detects: cough, sneeze, sniffle from 16kHz audio chunks.
    Uses AST Transformer predictions + Spectral Acoustic Analysis (ZCR, HFER, Centroid).
    """

    CATEGORIES = ["normal", "cough", "sneeze", "sniffle"]
    CONFIDENCE_THRESHOLD = 0.10  # Sensitive 10% threshold for audio detection

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
            # 1. Energy gate & Crest factor gate (filters silence and flat background room hum/static)
            rms = float(np.sqrt(np.mean(audio_data ** 2)))
            max_val = float(np.max(np.abs(audio_data)))
            crest_factor = max_val / (rms + 1e-12)

            if rms < 0.012 or crest_factor < 1.8:
                return self._fallback_result()

            # 2. Peak normalization
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

            # Weight multipliers to compensate for AudioSet dataset prior class imbalance
            WEIGHTS = {
                "cough": 1.0,
                "sneeze": 2.5,  # Boost sneeze sensitivity so sneezes compete fairly with coughs
                "sniffle": 1.2
            }

            category_scores: Dict[str, float] = {"normal": 1.0, "cough": 0.0, "sneeze": 0.0, "sniffle": 0.0}
            best_raw_prob = 0.0

            for idx, prob in enumerate(probs):
                label = self._label_map.get(idx, "")
                category = AUDIOSET_TO_RESPIRATORY.get(label)
                if category and category != "normal":
                    weighted_prob = float(prob) * WEIGHTS.get(category, 1.0)
                    category_scores[category] = max(category_scores[category], weighted_prob)
                    if float(prob) > best_raw_prob:
                        best_raw_prob = float(prob)

            # 4. Spectral acoustic feature analysis for Cough vs Sneeze disambiguation
            spectral_info = self._extract_spectral_features(norm_audio, sr)
            hfer = spectral_info["hfer"]
            centroid = spectral_info["spectral_centroid"]
            low_power = spectral_info["low_power_ratio"]
            zcr = spectral_info["zcr"]

            is_acoustic_sneeze = (hfer > 0.35 and centroid > 2200.0)
            is_acoustic_cough = (low_power > 0.55 and centroid < 2100.0)

            # Primary AST Model & Acoustic Gate:
            # Requires AST model prediction OR strong high-energy acoustic burst to prevent false triggers from ambient noise.
            has_valid_detection = (
                best_raw_prob >= 0.05 or 
                category_scores["cough"] >= 0.08 or 
                category_scores["sneeze"] >= 0.08 or 
                category_scores["sniffle"] >= 0.08 or
                (is_acoustic_sneeze and rms >= 0.02)
            )

            if not has_valid_detection:
                return self._fallback_result()

            detected_event = "normal"
            best_confidence = 0.0

            if (category_scores["sneeze"] >= 0.08 or is_acoustic_sneeze) and (category_scores["sneeze"] >= category_scores["cough"] or is_acoustic_sneeze):
                detected_event = "sneeze"
                best_confidence = max(category_scores["sneeze"], round(hfer, 4), 0.35)
            elif category_scores["cough"] >= 0.08 or is_acoustic_cough:
                detected_event = "cough"
                best_confidence = max(category_scores["cough"], round(low_power, 4), 0.35)
            elif category_scores["sniffle"] >= 0.08:
                detected_event = "sniffle"
                best_confidence = category_scores["sniffle"]

            if detected_event != "normal":
                category_scores["normal"] = max(0.0, 1.0 - best_confidence)

            return {
                "detected_event": detected_event,
                "confidence": round(best_confidence if detected_event != "normal" else 1.0, 4),
                "probabilities": {k: round(v, 4) for k, v in category_scores.items()},
                "spectral_features": {
                    "hfer": round(hfer, 4),
                    "spectral_centroid_hz": round(centroid, 1),
                    "low_power_ratio": round(low_power, 4),
                    "zcr": round(zcr, 4)
                }
            }

        except Exception as e:
            logger.error(f"AST inference error: {e}")
            return self._fallback_result()

    def _extract_spectral_features(self, audio_data: np.ndarray, sample_rate: int) -> Dict[str, float]:
        """
        Calculates High-Frequency Energy Ratio (HFER), Low-Power Ratio, Zero Crossing Rate (ZCR), and Spectral Centroid.
        - Cough: Low spectral centroid (<2000 Hz), Low HFER (<0.25), High low_power_ratio (>0.65)
        - Sneeze: High spectral centroid (>2100 Hz), High HFER (>0.25), High ZCR (>0.28) from nasal friction / release
        """
        if len(audio_data) == 0:
            return {"spectral_centroid": 0.0, "hfer": 0.0, "low_power_ratio": 0.0, "zcr": 0.0}

        fft_vals = np.abs(np.fft.rfft(audio_data))
        freqs = np.fft.rfftfreq(len(audio_data), 1.0 / sample_rate)

        total_energy = float(np.sum(fft_vals ** 2)) + 1e-12

        low_mask = freqs < 1800.0
        low_energy = float(np.sum(fft_vals[low_mask] ** 2))
        low_power_ratio = float(low_energy / total_energy)

        hf_mask = freqs >= 1800.0
        hf_energy = float(np.sum(fft_vals[hf_mask] ** 2))
        hfer = float(hf_energy / total_energy)

        spectral_centroid = float(np.sum(freqs * fft_vals) / (np.sum(fft_vals) + 1e-12))
        zcr = float(np.mean(np.abs(np.diff(np.sign(audio_data))))) / 2.0

        return {
            "spectral_centroid": spectral_centroid,
            "hfer": hfer,
            "low_power_ratio": low_power_ratio,
            "zcr": zcr
        }

    def _fallback_result(self) -> Dict[str, Any]:
        return {
            "detected_event": "normal",
            "confidence": 0.0,
            "probabilities": {"normal": 1.0, "cough": 0.0, "sneeze": 0.0, "sniffle": 0.0},
            "spectral_features": {"hfer": 0.0, "spectral_centroid_hz": 0.0, "low_power_ratio": 0.0, "zcr": 0.0}
        }


