from collections import deque
from typing import Dict, Any

class TemporalEmotionSmoother:
    """
    Fast Temporal Consensus Smoother for Real-Time Emotion Inference.
    Weighted dynamically to respond instantly (< 200ms) to expression changes.
    """

    def __init__(self, window_size: int = 2):
        self.window_size = window_size
        self.history = deque(maxlen=window_size)

    def update(self, raw_prediction: Dict[str, Any]) -> Dict[str, Any]:
        distribution = raw_prediction.get("distribution", {})
        if not distribution:
            return raw_prediction

        self.history.append(distribution)

        # Weighted moving average: 70% current frame, 30% previous frame for instant responsiveness
        if len(self.history) == 1:
            smoothed_dist = {k: round(v, 4) for k, v in distribution.items()}
        else:
            prev = self.history[0]
            curr = self.history[1]
            smoothed_dist = {}
            for emotion in distribution.keys():
                weighted_prob = (curr.get(emotion, 0.0) * 0.70) + (prev.get(emotion, 0.0) * 0.30)
                smoothed_dist[emotion] = round(weighted_prob, 4)

        dominant = max(smoothed_dist, key=smoothed_dist.get)
        confidence = smoothed_dist[dominant]

        # Clinical stress score (weighted combination of Sad, Fear, Disgust, Angry)
        stress_weights = {"Sad": 0.6, "Fear": 0.9, "Disgust": 0.7, "Angry": 0.8}
        raw_stress = sum(smoothed_dist.get(em, 0.0) * weight for em, weight in stress_weights.items())
        clinical_stress_score = round(min(1.0, raw_stress * 1.2), 2)

        return {
            "dominant_emotion": dominant,
            "confidence": confidence,
            "clinical_stress_score": clinical_stress_score,
            "distribution": smoothed_dist
        }
