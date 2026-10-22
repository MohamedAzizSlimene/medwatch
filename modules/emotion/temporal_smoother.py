import time
from collections import deque
from typing import Dict, Any, List, Optional
from core.config import settings


class SustainedEmotionTracker:
    """
    Short recency-weighted smoother + sustain gate for honest emotion tracking.

    Design goals:
    - Newest frames weigh more so expression changes show up in ~0.5–1s, not 3s.
    - A non-neutral emotion must stay dominant for ≥ SUSTAIN_THRESHOLD_FRAMES
      (~2s @ 10fps) before any observation is emitted.
    - A per-emotion cooldown prevents repeated triggering from the same sustained state.
    - No clinical_stress_score. No × 1.2 amplifier. Output is factual event strings only.
    """

    def __init__(
        self,
        window_size: int = None,
        sustain_threshold_frames: int = None,
        cooldown_s: float = None,
        stress_emotions: List[str] = None,
    ):
        self.window_size = window_size or settings.EMOTION_SMOOTHING_WINDOW
        self.sustain_threshold = sustain_threshold_frames or settings.EMOTION_SUSTAIN_THRESHOLD_FRAMES
        self.cooldown_s = cooldown_s or settings.EMOTION_SUSTAIN_COOLDOWN_S
        self.stress_emotions = stress_emotions or settings.EMOTION_STRESS_EMOTIONS

        # Rolling buffer: full distribution per frame for mean computation
        self._dist_history: deque = deque(maxlen=self.window_size)

        # Sustain counter: consecutive frames the current non-neutral dominant has held
        self._sustain_counter: int = 0
        self._sustain_current_emotion: Optional[str] = None
        self._sustain_start_time: Optional[float] = None

        # Per-emotion cooldown: maps emotion → timestamp of last emission
        self._last_emission: Dict[str, float] = {}

        # Active sustained events for this session (accumulates until reset)
        self._sustained_events: List[str] = []
        self._last_result: Optional[Dict[str, Any]] = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def update(self, raw_prediction: Dict[str, Any], face_detected: bool = True) -> Dict[str, Any]:
        """
        Consume one frame of raw ViT prediction.
        Returns enriched dict with:
          - distribution        : recency-weighted mean probabilities
          - dominant_emotion    : label after Neutral-margin rescue for Angry/Sad
          - confidence          : probability of the chosen class
          - sustained_events    : list of factual event strings emitted this session
          - observation_label   : most recent event string, or None
          - clinical_stress_score: None (explicitly removed)
        """
        distribution = raw_prediction.get("distribution", {})
        if not face_detected or not distribution:
            if self._last_result is not None:
                return {
                    **self._last_result,
                    "sustained_events": list(self._sustained_events),
                }
            return {
                **raw_prediction,
                "sustained_events": list(self._sustained_events),
                "observation_label": None,
                "clinical_stress_score": None,
            }

        # --- 1. Rolling mean over the buffer ---
        self._dist_history.append(distribution)
        smoothed_dist = self._compute_mean_distribution()
        smoothed_dist = self._lift_hard_class_peaks(smoothed_dist)

        # --- 2. Dominant emotion, with Neutral-margin rescue ---
        dominant, confidence = self._select_dominant(smoothed_dist)

        # --- 3. Sustain gate ---
        observation_label = self._tick_sustain_gate(dominant)

        result = {
            "dominant_emotion": dominant,
            "confidence": round(confidence, 4),
            "distribution": smoothed_dist,
            "sustained_events": list(self._sustained_events),
            "observation_label": observation_label,
            "clinical_stress_score": None,
        }
        self._last_result = result
        return result

    def reset(self):
        """Reset all session state (call when a new consultation session starts)."""
        self._dist_history.clear()
        self._sustain_counter = 0
        self._sustain_current_emotion = None
        self._sustain_start_time = None
        self._last_emission = {}
        self._sustained_events = []
        self._last_result = None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _compute_mean_distribution(self) -> Dict[str, float]:
        """Recency-weighted mean: newest frame has the most influence."""
        if not self._dist_history:
            return {}
        all_keys = self._dist_history[0].keys()
        n = len(self._dist_history)
        weights = [i + 1 for i in range(n)]
        total_w = sum(weights)
        return {
            key: round(
                sum(d.get(key, 0.0) * w for d, w in zip(self._dist_history, weights)) / total_w,
                4,
            )
            for key in all_keys
        }

    def _lift_hard_class_peaks(self, mean_dist: Dict[str, float]) -> Dict[str, float]:
        """Keep a recent Angry/Sad spike visible instead of averaging it away."""
        if not self._dist_history or not mean_dist:
            return mean_dist

        recent = list(self._dist_history)[-4:]
        lifted = dict(mean_dist)
        for key in ("Angry", "Sad"):
            peak = max(d.get(key, 0.0) for d in recent)
            lifted[key] = round(max(lifted.get(key, 0.0), 0.50 * lifted.get(key, 0.0) + 0.50 * peak), 4)

        total = sum(lifted.values()) or 1.0
        return {key: round(value / total, 4) for key, value in lifted.items()}

    def _select_dominant(self, dist: Dict[str, float]) -> tuple:
        """Prefer Angry/Sad when Neutral only wins by a small margin."""
        ranked = sorted(dist.items(), key=lambda item: item[1], reverse=True)
        top_label, top_prob = ranked[0]
        if top_label != "Neutral":
            return top_label, top_prob

        margin = settings.EMOTION_NEUTRAL_MARGIN
        min_prob = settings.EMOTION_HARD_MIN_PROB
        for label, prob in ranked[1:]:
            if label in self.stress_emotions and prob >= min_prob and (top_prob - prob) <= margin:
                return label, prob
        return top_label, top_prob

    def _tick_sustain_gate(self, dominant: str) -> Optional[str]:
        """
        Increment or reset the sustain counter based on current dominant emotion.
        Emits an observation string when the threshold is crossed (subject to cooldown).
        Returns the emitted string, or None.
        """
        if dominant not in self.stress_emotions:
            # Neutral / Happy / Surprise → reset sustain counter
            self._sustain_counter = 0
            self._sustain_current_emotion = None
            self._sustain_start_time = None
            return None

        if dominant == self._sustain_current_emotion:
            # Same non-neutral emotion continues → increment counter
            self._sustain_counter += 1
        else:
            # Switched to a different non-neutral emotion → restart counter
            self._sustain_counter = 1
            self._sustain_current_emotion = dominant
            self._sustain_start_time = time.monotonic()

        if self._sustain_counter >= self.sustain_threshold:
            return self._maybe_emit(dominant)

        return None

    def _maybe_emit(self, emotion: str) -> Optional[str]:
        """
        Emit a factual observation string if the per-emotion cooldown has expired.
        Resets the counter so the gate re-arms after cooldown elapses.
        """
        now = time.monotonic()
        last = self._last_emission.get(emotion, 0.0)

        if (now - last) < self.cooldown_s:
            return None  # Still within cooldown

        start = self._sustain_start_time or now
        duration_s = round(now - start, 1)

        event_str = f"{emotion} expression sustained for {duration_s}s"
        self._sustained_events.append(event_str)
        self._last_emission[emotion] = now

        # Reset counter so gate re-arms cleanly
        self._sustain_counter = 0
        self._sustain_start_time = None

        return event_str

