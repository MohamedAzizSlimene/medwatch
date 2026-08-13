# 🏥 MedWatch — Real-Time AI Medical Monitoring Engine

MedWatch is a high-performance, real-time AI backend microservice designed for video medical consultations. It processes streamed webcam frames and audio chunks to provide real-time clinical insights and patient monitoring.

## 🧠 Active AI Modules

1. **🫁 Respiratory Health Monitoring (`modules/respiratory/`)**
   - **Audio Classifier (BEATs / AST)**: Detects coughing, sneezing, and sniffling events.
   - **Visual Gesture Analysis**: Tracks hand-to-nose and hand-to-face activity using pose estimation.
2. **😊 Facial Emotion & Stress Recognition (`modules/emotion/`)**
   - **Vision Transformer (ViT-Base)** pre-trained on AffectNet+ (soft labels).
   - Clinical Stress Score with 3-frame temporal consensus & Kalman filtering.
3. **😴 Fatigue & Drowsiness Detection (`modules/fatigue/`)**
   - **YOLOv8** Face Detection + **PFLD** 98-Point Facial Landmarks.
   - Standard **PERCLOS** (percentage eye closure over 60s rolling window) & Mouth Aspect Ratio (yawn dynamics).
4. **🔗 Multi-Modal Fusion Engine (`modules/fusion/`)**
   - Combines respiratory, emotional, and fatigue metrics into a unified **Clinical Risk Score** and live alert notifications.

---

## ⚡ Quick Start

### Installation

```bash
# Create and activate virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Running the AI Backend Server

```bash
# Start FastAPI WebSocket & REST server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### API Endpoints

- **`GET /health`**: Healthcheck diagnostic endpoint.
- **`WS /ws/stream`**: Real-time WebSocket connection for streaming webcam video frames and audio chunks.
