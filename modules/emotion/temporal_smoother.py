import time
from collections import deque
from typing import Dict, Any, List, Optional
from core.config import settings


class SustainedEmotionTracker:
    """
    30-frame rolling mean smoother + 3-second sustain gate for honest emotion tracking.

    Design goals:
    - Single noisy frames (squinting, brief grimace) have ≤ 3.3% weight → no false spikes.
    - A non-neutral emotion must be the rolling dominant for ≥ SUSTAIN_THRESHOLD_FRAMES
      consecutive frames (default 90 ≈ 3s @ 30fps) before any observation is emitted.
    - A per-emotion 10s cooldown prevents repeated triggering from the same sustained state.
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

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def update(self, raw_prediction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Consume one frame of raw ViT prediction.
        Returns enriched dict with:
          - distribution        : 30-frame mean probabilities
          - dominant_emotion    : label of highest mean-probability class
          - confidence          : mean probability of dominant class
          - sustained_events    : list of factual event strings emitted this session
          - observation_label   : most recent event string, or None
          - clinical_stress_score: None (explicitly removed)
        """
        distribution = raw_prediction.get("distribution", {})
        if not distribution:
            return {
                **raw_prediction,
                "sustained_events": list(self._sustained_events),
                "observation_label": None,
                "clinical_stress_score": None,
            }

        # --- 1. Rolling mean over the buffer ---
        self._dist_history.append(distribution)
        smoothed_dist = self._compute_mean_distribution()

        # --- 2. Dominant emotion from smoothed distribution ---
        dominant = max(smoothed_dist, key=smoothed_dist.get)
        confidence = smoothed_dist[dominant]

        # --- 3. Sustain gate ---
        observation_label = self._tick_sustain_gate(dominant)

        return {
            "dominant_emotion": dominant,
            "confidence": round(confidence, 4),
            "distribution": smoothed_dist,
            "sustained_events": list(self._sustained_events),
            "observation_label": observation_label,
            "clinical_stress_score": None,
        }

    def reset(self):
        """Reset all session state (call when a new consultation session starts)."""
        self._dist_history.clear()
        self._sustain_counter = 0
        self._sustain_current_emotion = None
        self._sustain_start_time = None
        self._last_emission = {}
        self._sustained_events = []

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _compute_mean_distribution(self) -> Dict[str, float]:
        """Simple unweighted mean across the rolling buffer."""
        if not self._dist_history:
            return {}
        all_keys = self._dist_history[0].keys()
        n = len(self._dist_history)
        return {
            key: round(sum(d.get(key, 0.0) for d in self._dist_history) / n, 4)
            for key in all_keys
        }

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

