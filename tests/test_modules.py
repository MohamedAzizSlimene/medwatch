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
    assert "dominant_emotion" in res
    assert "clinical_stress_score" in res
    assert 0.0 <= res["clinical_stress_score"] <= 1.0
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
    
    resp_data = {"respiratory_event": "cough", "hand_to_nose_active": True}
    emo_data = {"clinical_stress_score": 0.7}
    fatigue_data = {"perclos_score": 0.20}
    
    res = fusion.analyze({
        "respiratory": resp_data,
        "emotion": emo_data,
        "fatigue": fatigue_data
    })
    
    assert "overall_risk_score" in res
    assert "risk_level" in res
    assert res["overall_risk_score"] > 0.0
    assert len(res["active_alerts"]) > 0
    print("[OK] FusionAnalyzer test passed.")

if __name__ == "__main__":
    test_respiratory_analyzer()
    test_emotion_analyzer()
    test_fatigue_analyzer()
    test_fusion_analyzer()
    print("\nAll module unit tests passed successfully!")
