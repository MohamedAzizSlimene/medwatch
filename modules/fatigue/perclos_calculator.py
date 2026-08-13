import time
from collections import deque
from typing import Dict, Any

class PERCLOSCalculator:
    """
    Yawn Dynamics & Fatigue Calculator.
    Links fatigue classification strictly to yawning activity (MAR & Yawn Frequency).
    
    - Status = 'FATIGUED' if currently yawning or yawn_count >= 3.
    - Status = 'MILDLY FATIGUED' if yawn_count is 1 or 2.
    - Status = 'NORMAL' if yawn_count == 0.
    """

    def __init__(self, window_seconds: int = 180, mar_yawn_threshold: float = 0.45):
        self.window_seconds = window_seconds
        self.mar_yawn_threshold = mar_yawn_threshold
        
        self.buffer = deque()
        self.yawn_count = 0
        self.last_yawn_time = 0.0

    def add_reading(self, mean_ear: float = 0.32, mar: float = 0.18, timestamp: float = None) -> Dict[str, Any]:
        if timestamp is None:
            timestamp = time.time()

        is_yawn = mar > self.mar_yawn_threshold

        # Yawn frequency tracking with 2.5s refractory debounce per yawn
        if is_yawn and (timestamp - self.last_yawn_time > 2.5):
            self.yawn_count += 1
            self.last_yawn_time = timestamp

        self.buffer.append((timestamp, is_yawn))

        # Evict readings outside rolling window (3 minutes)
        cutoff_time = timestamp - self.window_seconds
        while self.buffer and self.buffer[0][0] < cutoff_time:
            self.buffer.popleft()

        # Fatigue status strictly linked to Yawning
        if is_yawn or self.yawn_count >= 3:
            status = "FATIGUED"
        elif self.yawn_count >= 1:
            status = "MILDLY FATIGUED"
        else:
            status = "NORMAL"

        return {
            "perclos_score": round(float(self.yawn_count / 5.0), 2),  # Yawn fatigue index (0.0 to 1.0)
            "status": status,
            "yawn_count": self.yawn_count,
            "is_yawning_now": bool(is_yawn),
            "mar": round(float(mar), 3)
        }
