import os
import numpy as np
import torch
from PIL import Image
from typing import Dict, Any, Optional
from transformers import ViTForImageClassification, ViTImageProcessor
from core.logging import logger


class ViTEmotionClassifier:
    """
    Vision Transformer (ViT-Base) Facial Emotion Classifier.
    Pre-trained on AffectNet+ — model: trpakov/vit-face-expression
    Outputs 7 emotion probability scores + dominant emotion.

    Label mapping from model config:
        0: Angry, 1: Disgust, 2: Fear, 3: Happy, 4: Neutral, 5: Sad, 6: Surprise
    """

    def __init__(self, model_path: str = "models/emotion/vit_affectnet"):
        self.model_path = model_path
        self.is_loaded = False
        self.model: Optional[ViTForImageClassification] = None
        self.processor: Optional[ViTImageProcessor] = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.labels = ["Angry", "Disgust", "Fear", "Happy", "Neutral", "Sad", "Surprise"]

    def load(self) -> bool:
        try:
            if not os.path.exists(self.model_path):
                logger.error(f"ViT model folder not found at: {self.model_path}")
                return False

            logger.info(f"Loading ViT Emotion model from {self.model_path} on {self.device}...")
            self.processor = ViTImageProcessor.from_pretrained(self.model_path)
            self.model = ViTForImageClassification.from_pretrained(self.model_path)
            self.model.to(self.device)
            self.model.eval()

            # Set labels from model config (handles int or str dictionary keys)
            if hasattr(self.model.config, "id2label") and self.model.config.id2label:
                id2l = self.model.config.id2label
                self.labels = [
                    str(id2l.get(i, id2l.get(str(i), str(i)))).capitalize()
                    for i in range(len(id2l))
                ]

            self.is_loaded = True
            logger.info(f"ViT Emotion model loaded successfully. Labels: {self.labels}")
            return True

        except Exception as e:
            logger.error(f"Failed to load ViT Emotion model: {e}")
            self.is_loaded = False
            return False

    def predict_emotion(self, face_image_rgb: Optional[np.ndarray]) -> Dict[str, Any]:
        """
        Runs ViT inference on a cropped face image (RGB numpy array).
        Returns emotion probabilities and dominant emotion.
        """
        if not self.is_loaded or face_image_rgb is None or face_image_rgb.size == 0:
            return self._fallback_result()

        try:
            # Convert numpy array → PIL Image → ViT processor tensor
            pil_image = Image.fromarray(face_image_rgb.astype(np.uint8))
            inputs = self.processor(images=pil_image, return_tensors="pt").to(self.device)

            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits  # shape: [1, 7]
                probs = torch.softmax(logits, dim=-1).squeeze().cpu().numpy()

            # Build probability distribution dict
            distribution = {
                label: round(float(prob), 4)
                for label, prob in zip(self.labels, probs)
            }

            dominant_idx = int(np.argmax(probs))
            dominant_emotion = self.labels[dominant_idx]
            confidence = float(probs[dominant_idx])

            return {
                "dominant_emotion": dominant_emotion,
                "confidence": round(confidence, 4),
                "distribution": distribution
            }

        except Exception as e:
            logger.error(f"ViT inference error: {e}")
            return self._fallback_result()

    def _fallback_result(self) -> Dict[str, Any]:
        """Returns neutral fallback when face is not detected or model not loaded."""
        return {
            "dominant_emotion": "Neutral",
            "confidence": 0.0,
            "distribution": {e: (1.0 if e == "Neutral" else 0.0) for e in self.labels}
        }
