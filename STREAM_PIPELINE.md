# WebSocket Stream Pipeline - What Models Run

When the frontend sends video + audio to `ws://localhost:8001/ws/stream`, here's **exactly** what happens:

---

## The Complete Pipeline

```
FRONTEND SENDS:
├── frame_b64 (JPEG image)
└── audio_b64 (float32 audio chunk)

        ↓↓↓ BACKEND PROCESSES ↓↓↓

STEP 1: FATIGUE ANALYZER
├── Model: YOLOv8 Face Detector
│   └── Detects face in the image → face_bbox (bounding box)
│
├── Model: MediaPipe FaceLandmarker
│   └── Extracts eye/mouth landmarks from face → EAR (Eye Aspect Ratio) & MAR (Mouth Aspect Ratio)
│
└── PERCLOS Calculator (no model, just math)
    └── Tracks EAR over 60 seconds → drowsiness score

OUTPUT:
{
  "perclos_score": 0.03,
  "status": "NORMAL",
  "yawn_count": 0,
  "ear": 0.32,
  "mar": 0.16,
  "face_bbox": [x1, y1, x2, y2]
}

---

STEP 2: EMOTION ANALYZER
├── Model: YOLOv8 Face Detector (REUSES face_bbox from Step 1)
│   └── Crops face from image
│
├── Model: Vision Transformer (ViT-Base) on AffectNet+
│   └── Classifies 7 emotions: Angry, Disgust, Fear, Happy, Neutral, Sad, Surprise
│
└── Sustained Emotion Tracker (30-frame rolling window)
    └── Smooths emotional fluctuations

OUTPUT:
{
  "dominant_emotion": "Neutral",
  "confidence": 0.91,
  "distribution": {
    "Angry": 0.02,
    "Disgust": 0.00,
    "Fear": 0.00,
    "Happy": 0.05,
    "Neutral": 0.91,
    "Sad": 0.01,
    "Surprise": 0.00
  },
  "sustained_events": [ ... ],
  "observation_label": "neutral"
}

---

STEP 3: RESPIRATORY ANALYZER
├── AUDIO BRANCH:
│   └── Model: AST (Audio Spectrogram Transformer)
│       └── Classifies audio: cough, sneeze, sniffle, or normal
│
└── VISUAL BRANCH:
    ├── Model: YOLOv8 Face Detector (REUSES face_bbox from Step 1)
    └── Model: MediaPipe HandLandmarker
        └── Detects hand positions
        └── Checks if hand is near nose (hand-to-nose gesture)

OUTPUT:
{
  "respiratory_event": "normal",
  "audio_confidence": 1.0,
  "hand_to_nose_active": false,
  "hand_to_nose_count": 0,
  "cumulative_counts": {
    "cough": 0,
    "sneeze": 0,
    "sniffle": 0,
    "hand_to_nose": 0
  }
}

---

STEP 4: FUSION ANALYZER
├── Takes respiratory_res, emotion_res, fatigue_res
└── Weighted combination:
    ├── Respiratory: 40%
    ├── Emotion/Stress: 30%
    └── Fatigue: 30%
    └── Calculates overall_risk_score (0.0 - 1.0)

OUTPUT:
{
  "overall_risk_score": 0.31,
  "risk_level": "MEDIUM",
  "sub_scores": {
    "respiratory": 0.0,
    "stress": 0.04,
    "fatigue": 1.0
  },
  "active_alerts": [ "Significant Drowsiness / PERCLOS Alert" ]
}

        ↓↓↓ BACKEND SENDS BACK ↓↓↓

RESPONSE TO FRONTEND:
{
  "timestamp": 1692547200.123,
  "respiratory": { ... },
  "emotion": { ... },
  "fatigue": { ... },
  "fusion": { ... }
}
```

---

## Models Used (Summary)

| Module | Models Used | Input | Output |
|--------|-------------|-------|--------|
| **Fatigue** | YOLOv8, MediaPipe FaceLandmarker | Video frame | PERCLOS, EAR, MAR, yawn_count |
| **Emotion** | YOLOv8, ViT-Base (AffectNet+) | Video frame | 7 emotion probabilities |
| **Respiratory** | AST (Audio Transformer), YOLOv8, MediaPipe HandLandmarker | Audio + Video | Cough/Sneeze/Sniffle + Hand-to-nose |
| **Fusion** | Rule-based (no ML model) | All 3 outputs above | Combined risk score |

---

## Model Files Location

```
models/
├── fatigue/
│   ├── yolov8n-face.pt              ← YOLOv8 face detector
│   └── face_landmarker.task         ← MediaPipe FaceLandmarker
│
├── emotion/
│   └── vit_affectnet/
│       ├── config.json
│       ├── model.safetensors        ← ViT-Base emotion classifier
│       └── preprocessor_config.json
│
└── respiratory/
    ├── ast_audioset/
    │   ├── config.json
    │   ├── model.safetensors        ← AST audio classifier
    │   └── preprocessor_config.json
    └── hand_landmarker.task         ← MediaPipe HandLandmarker
```

---

## What Happens Every Frame (Every ~100ms)

```
Timeline:

t=0ms    → Frontend sends: {frame_b64, audio_b64}
         ↓
t=5ms    → YOLOv8 runs (detects face) → face_bbox
         ↓
t=15ms   → MediaPipe FaceLandmarker runs (eye/mouth ratios)
         ↓
t=20ms   → ViT Emotion runs (emotion classification)
         ↓
t=30ms   → AST Audio runs (cough/sneeze detection)
         ↓
t=35ms   → MediaPipe HandLandmarker runs (hand positions)
         ↓
t=40ms   → Fusion calculates overall risk
         ↓
t=45ms   → Backend sends result back to frontend
         ↓
t=100ms  → Next frame arrives from frontend

Total latency: ~45-50ms per frame
```

---

## Key Points

1. **All models run ON EVERY FRAME** - They process video + audio simultaneously
2. **Face detection (YOLOv8) runs once** - Result is reused by emotion and fatigue modules
3. **Four separate neural networks**:
   - YOLOv8 (face detection)
   - ViT (emotion classification)
   - AST (audio classification)
   - MediaPipe (landmarks - not deep learning, geometric)
4. **No separate REST endpoints for individual modules** - Everything goes through the WebSocket stream
5. **Models are loaded at server startup** - They stay in memory the whole time

---

## If Frontend Engineer Asks "Which Models Do You Use?"

Answer:
- **YOLOv8 (nano)** - Face detection
- **ViT-Base trained on AffectNet+** - Emotion (7 emotions)
- **AST (Audio Spectrogram Transformer)** - Audio events (cough/sneeze/sniffle)
- **MediaPipe** - Face landmarks, hand landmarks
- **Fusion Engine** - Rule-based combination (no ML model)

All run in parallel per frame through the WebSocket stream.
