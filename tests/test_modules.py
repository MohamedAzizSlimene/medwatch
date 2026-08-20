import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
from modules.respiratory import RespiratoryAnalyzer
from modules.emotion import EmotionAnalyzer
from modules.fatigue import FatigueAnalyzer
from modules.fusion import FusionAnalyzer

def test_respiratory_analyzer():
    analyzer = RespiratoryAnalyzer()
    analyzer.load_model()
    
    # Test visual hand to nose detection (within 45px threshold)
    res = analyzer.analyze({
        "nose_coords": (100, 100),
        "wrist_coords": (110, 105)  # Distance = ~11.2px, should be True
    })
    
    assert "respiratory_event" in res
    assert "hand_to_nose_active" in res
    print(f"   Hand-to-nose detection: {res['hand_to_nose_active']}")
    assert bool(res["hand_to_nose_active"]) is True, f"Expected True but got {res['hand_to_nose_active']}"

    # Test audio sneeze classification
    sr = 16000
    t = np.linspace(0, 1.0, sr)
    sneeze_chunk = (np.random.normal(0, 0.3, len(t)) * np.exp(-1.5 * t) + 0.3 * np.sin(2 * np.pi * 2800 * t) * np.exp(-2 * t)).astype(np.float32)
    sneeze_res = analyzer.analyze({"audio_chunk": sneeze_chunk})
    assert sneeze_res["respiratory_event"] == "sneeze", f"Expected sneeze but got {sneeze_res['respiratory_event']}"
    print(f"   Sneeze audio classification: {sneeze_res['respiratory_event']} (conf: {sneeze_res['audio_confidence']})")
    print("[OK] RespiratoryAnalyzer test passed.")

def test_emotion_analyzer():
    analyzer = EmotionAnalyzer()
    analyzer.load_model()
    
    dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    res = analyzer.analyze({"frame": dummy_frame})
    assert "dominant_emotion" in res, "Missing dominant_emotion"
    assert "distribution" in res, "Missing distribution"
    assert "sustained_events" in res, "Missing sustained_events (SustainedEmotionTracker)"
    assert isinstance(res["sustained_events"], list), "sustained_events should be a list"
    # clinical_stress_score is removed — confirm it's None or absent
    assert res.get("clinical_stress_score") is None, "clinical_stress_score should be None"
    print("[OK] EmotionAnalyzer test passed.")

def test_fatigue_analyzer():
    analyzer = FatigueAnalyzer()
    analyzer.load_model()
    
    dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    res = analyzer.analyze({"frame": dummy_frame})
    assert "perclos_score" in res
    assert "status" in res
    print("[OK] FatigueAnalyzer test passed.")

def test_fusion_analyzer():
    fusion = FusionAnalyzer()
    fusion.load_model()

    resp_data = {"respiratory_event": "cough", "hand_to_nose_active": True,
                 "cumulative_counts": {"cough": 3, "sneeze": 0, "hand_to_nose": 0}}
    # New: emotion data uses sustained_events instead of clinical_stress_score
    emo_data = {
        "dominant_emotion": "Sad",
        "sustained_events": ["Sad expression sustained for 4.1s"],
        "observation_label": "Sad expression sustained for 4.1s",
        "clinical_stress_score": None
    }
    fatigue_data = {"yawn_count": 0, "status": "NORMAL", "is_yawning_now": False}

    res = fusion.analyze({
        "respiratory": resp_data,
        "emotion": emo_data,
        "fatigue": fatigue_data
    })

    assert "session_status" in res, "Missing session_status"
    assert "active_observations" in res, "Missing active_observations"
    assert len(res["active_observations"]) > 0, "Expected at least one observation (coughs + sustained emotion)"
    print("[OK] FusionAnalyzer test passed.")

if __name__ == "__main__":
    test_respiratory_analyzer()
    test_emotion_analyzer()
    test_fatigue_analyzer()
    test_fusion_analyzer()
    print("\nAll module unit tests passed successfully!")
