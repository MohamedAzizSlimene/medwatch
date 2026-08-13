# 🏥 MedWatch — Medical Video Consultation AI Platform
## Complete Rebuild Architecture Plan

> **Document Version:** 1.0  
> **Date:** August 2026  
> **Status:** Architecture Design Phase  
> **Project Codename:** MedWatch

---

## 📋 Executive Summary

This document outlines the **complete rebuild** of the patient video consultation monitoring system. The current prototype (Flask + DeepFace + YAMNet) has fundamental limitations: generic models not designed for medical use, no real-time streaming, no data persistence, monolithic frontend, and no clinical validation.

The new system — **MedWatch** — will be built from zero using **Clean Architecture**, medical-grade AI models, real-time WebRTC streaming, and a modern React frontend. Every component is chosen for clinical relevance, performance, and maintainability.

---

## 🔍 Why Rebuild? — Current System Limitations

| Problem | Current State | Impact |
|---------|--------------|--------|
| **Respiratory Detection** | YAMNet (generic YouTube audio classifier) | ~50-60% accuracy, high false positives |
| **Emotion Detection** | DeepFace (not clinical-grade) | ~65-75%, no temporal smoothing, slow (200-500ms) |
| **Fatigue Detection** | MediaPipe + custom heuristics | Not clinically validated, no PERCLOS |
| **Architecture** | Flask monolith, no separation of concerns | Hard to maintain, test, or scale |
| **Streaming** | HTTP polling (base64 frames every 3s) | High latency, wasteful bandwidth |
| **Data Persistence** | None | No session history, no analytics |
| **Frontend** | 5000+ lines vanilla JS in single file | Unmaintainable, no component reuse |
| **Security** | None | No auth, no encryption, no HIPAA compliance |

---

## 🏗️ New System Architecture

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          CLIENT (Next.js + React)                       │
│  ┌──────────┐  ┌───────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ Video    │  │ Dashboard │  │ Session      │  │ Patient          │  │
│  │ Call UI  │  │ Panels    │  │ Management   │  │ History          │  │
│  └────┬─────┘  └─────┬─────┘  └──────┬───────┘  └────────┬─────────┘  │
│       │              │               │                    │            │
│       │         WebSocket (wss://)   REST API (HTTPS)     │            │
└───────┼──────────────┼───────────────┼────────────────────┼────────────┘
        │              │               │                    │
   WebRTC/LiveKit      │               │                    │
        │              │               │                    │
┌───────┼──────────────┼───────────────┼────────────────────┼────────────┐
│       ▼              ▼               ▼                    ▼            │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    API GATEWAY (FastAPI)                         │   │
│  │  ┌──────────┐  ┌──────────────┐  ┌──────────┐  ┌────────────┐ │   │
│  │  │ Auth     │  │ Session      │  │ Patient  │  │ WebSocket  │ │   │
│  │  │ Routes   │  │ Routes       │  │ Routes   │  │ Handler    │ │   │
│  │  └──────────┘  └──────────────┘  └──────────┘  └────────────┘ │   │
│  └─────────────────────────┬───────────────────────────────────────┘   │
│                            │                                           │
│  ┌─────────────────────────▼───────────────────────────────────────┐   │
│  │                   APPLICATION LAYER (Use Cases)                  │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌───────────────────────┐ │   │
│  │  │ Start        │  │ Process      │  │ Generate              │ │   │
│  │  │ Session      │  │ Analysis     │  │ Report                │ │   │
│  │  └──────────────┘  └──────────────┘  └───────────────────────┘ │   │
│  └─────────────────────────┬───────────────────────────────────────┘   │
│                            │                                           │
│  ┌─────────────────────────▼───────────────────────────────────────┐   │
│  │                     DOMAIN LAYER (Pure Python)                   │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌──────────────────────┐   │   │
│  │  │ Entities    │  │ Value       │  │ Domain               │   │   │
│  │  │ (Patient,   │  │ Objects     │  │ Events               │   │   │
│  │  │  Session)   │  │ (Vitals,    │  │ (CoughDetected,      │   │   │
│  │  │             │  │  Emotion)   │  │  FatigueAlert)       │   │   │
│  │  └─────────────┘  └─────────────┘  └──────────────────────┘   │   │
│  └─────────────────────────┬───────────────────────────────────────┘   │
│                            │                                           │
│  ┌─────────────────────────▼───────────────────────────────────────┐   │
│  │                  INFRASTRUCTURE LAYER                            │   │
│  │  ┌────────────┐ ┌──────────┐ ┌───────────┐ ┌────────────────┐  │   │
│  │  │ AI Engine  │ │ Database │ │ LiveKit   │ │ Auth           │  │   │
│  │  │ (Models)   │ │ (Postgres│ │ (WebRTC)  │ │ (JWT/OAuth)    │  │   │
│  │  │            │ │  + Redis)│ │           │ │                │  │   │
│  │  └──────┬─────┘ └──────────┘ └───────────┘ └────────────────┘  │   │
│  └─────────┼───────────────────────────────────────────────────────┘   │
│            │                                                           │
│  ┌─────────▼───────────────────────────────────────────────────────┐   │
│  │              AI PROCESSING PIPELINE                              │   │
│  │                                                                  │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐    │   │
│  │  │ RESPIRATORY  │  │ FACIAL       │  │ FATIGUE &          │    │   │
│  │  │ ────────────│  │ ────────────│  │ VITALS             │    │   │
│  │  │ BEATs/AST   │  │ ViT +       │  │ ──────────────     │    │   │
│  │  │ Fine-tuned  │  │ AffectNet+  │  │ MediaPipe +        │    │   │
│  │  │ on ICBHI    │  │             │  │ PERCLOS + rPPG     │    │   │
│  │  └──────────────┘  └──────────────┘  └────────────────────┘    │   │
│  │                                                                  │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐    │   │
│  │  │ PAIN         │  │ MULTI-MODAL  │  │ TEMPORAL           │    │   │
│  │  │ DETECTION    │  │ FUSION       │  │ SMOOTHING          │    │   │
│  │  │ ──────────  │  │ ──────────  │  │ ─────────────      │    │   │
│  │  │ ConvNeXt +  │  │ XGBoost /   │  │ Sliding Window +   │    │   │
│  │  │ LSTM        │  │ Attention   │  │ Kalman Filter      │    │   │
│  │  └──────────────┘  └──────────────┘  └────────────────────┘    │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│                        BACKEND SERVER                                   │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🧠 AI Models — What to Use and Why

This is the core of the system. Each model was selected based on extensive research of the 2025-2026 state-of-the-art.

### 1. 🫁 Respiratory Sound Analysis

| Aspect | Old (YAMNet) | New (BEATs / AST) |
|--------|-------------|-------------------|
| **Type** | Generic YouTube audio classifier | Medical audio transformer |
| **Training Data** | AudioSet (YouTube) | Pre-trained on AudioSet → Fine-tuned on **ICBHI 2017** |
| **Classes** | 600+ generic sounds | 4 medical classes: Normal, Crackle, Wheeze, Both |
| **Accuracy** | ~50-60% for respiratory | **~85-92%** (with patient-aware split) |
| **Architecture** | CNN-based | Transformer with self-attention |

#### Recommended Model: **BEATs (Bidirectional Encoder from Audio Transformers)**

- **Why BEATs over YAMNet?**
  - 90M parameter transformer pre-trained on large-scale audio
  - State-of-the-art on ICBHI benchmark when fine-tuned
  - Captures long-range temporal dependencies (critical for respiratory cycles)
  - Available on HuggingFace: `microsoft/beats-audio-base`

- **Do we need to train our own?** ✅ **YES — Fine-tuning required**
  - Download BEATs pre-trained weights
  - Fine-tune on **ICBHI 2017 Respiratory Sound Database** (920 recordings, 6,898 breath cycles)
  - Use **patient-aware GroupShuffleSplit** (CRITICAL — prevents data leakage)
  - Add **audio enhancement preprocessing** (CMGAN-based noise reduction) before classification
  - Expected result: **~87-90% balanced accuracy** on 4-class classification

- **Alternative (Simpler):** Audio Spectrogram Transformer (AST)
  - `MIT/ast-finetuned-audioset` on HuggingFace
  - Slightly easier to fine-tune, slightly lower accuracy
  - Good fallback if BEATs proves too resource-heavy

- **Input Pipeline:**
  ```
  Raw Audio → Noise Reduction (CMGAN) → Resample 16kHz → Log-Mel Spectrogram → BEATs → Classification
  ```

- **Detection Window:** 10-30 seconds (vs. current 3 seconds) for full respiratory cycles

---

### 2. 😊 Facial Emotion & Expression Recognition

| Aspect | Old (DeepFace) | New (ViT + AffectNet+) |
|--------|---------------|----------------------|
| **Type** | Wrapper library (multiple backends) | Vision Transformer purpose-trained |
| **Training Data** | FER2013 (limited, noisy) | **AffectNet+** (soft labels, 400K+ images) |
| **Architecture** | VGG-Face / OpenFace | **ViT-Base** or **Swin Transformer** |
| **Speed** | 200-500ms per frame | **30-80ms** (quantized INT8) |
| **Accuracy** | ~65-75% | **~80-88%** |

#### Recommended Model: **Vision Transformer (ViT-Base) pre-trained on AffectNet+**

- **Why ViT over DeepFace?**
  - Captures global facial context (not just local features)
  - AffectNet+ uses **soft labels** → much more reliable for clinical settings
  - Handles occlusion (masks, glasses) better than CNN-based methods
  - Lighter and faster when quantized (INT8)

- **Do we need to train our own?** ❌ **NO for the base** — ⚠️ **YES for clinical fine-tuning (optional)**
  - Start with `ViT-Base` pre-trained on AffectNet+ (available on HuggingFace)
  - Optionally fine-tune on medical consultation recordings if available
  - Add **temporal smoothing** (require 3+ consecutive predictions before reporting)

- **Enhanced Emotion Categories for Medical Use:**
  - Standard: Happy, Sad, Angry, Neutral, Surprise, Fear, Disgust
  - **NEW clinical additions:** Anxiety, Discomfort, Confusion, Pain-related expressions
  - Map emotions to clinical stress scores with confidence intervals

- **Input Pipeline:**
  ```
  Video Frame → Face Detection (MediaPipe) → Crop & Align → ViT → Emotion + Confidence
                                                              ↓
                                              Temporal Smoothing (3-frame consensus)
                                                              ↓
                                              Clinical Stress Score (with CI)
  ```

---

### 3. 😣 Pain Detection (NEW — Not in Current System)

| Aspect | Details |
|--------|---------|
| **Architecture** | ConvNeXt backbone + LSTM for temporal analysis |
| **Training Data** | UNBC-McMaster Shoulder Pain dataset |
| **Classes** | Pain intensity (0-10 scale) or Binary (pain/no-pain) |
| **Accuracy** | ~75-85% for binary, ~70-80% for intensity |

#### Recommended Model: **ConvNeXt + LSTM Hybrid**

- **Why add pain detection?**
  - Critical for non-verbal patients (ICU, cognitive impairment)
  - Directly relevant to medical consultations
  - Complements emotion detection for holistic patient assessment

- **Do we need to train our own?** ✅ **YES — Custom training required**
  - No off-the-shelf "pain detector" exists with acceptable clinical accuracy
  - Use ConvNeXt as backbone (pre-trained on ImageNet)
  - Fine-tune on UNBC-McMaster + optionally a clinical dataset
  - Add LSTM layer for temporal pain dynamics (pain is not a single-frame phenomenon)

---

### 4. 😴 Fatigue & Drowsiness Detection

| Aspect | Old (Custom Heuristics) | New (YOLOv8 + PERCLOS + LSTM) |
|--------|------------------------|-------------------------------|
| **Face Detection** | MediaPipe only | **YOLOv8** (faster, more robust) |
| **Eye Analysis** | Simple EAR threshold | **PERCLOS standard** (% closure over 60s) |
| **Temporal** | None | **LSTM** for temporal fatigue patterns |
| **Yawn Detection** | Mouth ratio > 0.38 | **Mouth Aspect Ratio + duration + frequency** |
| **Head Pose** | None | **Head pose analysis** (nodding detection) |

#### Recommended Approach: **YOLOv8 + PFLD + LSTM**

- **Do we need to train our own?** ⚠️ **PARTIAL**
  - YOLOv8 face detection: Use pre-trained (no training needed)
  - PFLD (Practical Facial Landmark Detector): Use pre-trained
  - LSTM for temporal analysis: **Train on NTHU-DDD dataset** (drowsy driving dataset, adaptable to medical)
  - Combine with MediaPipe for hand-to-face detection (keep from current system)

- **PERCLOS Implementation:**
  ```
  EAR (Eye Aspect Ratio) → Rolling 60-second window
                          → % frames where eyes >80% closed
                          → PERCLOS score
                          → Fatigue classification (Alert / Mildly Fatigued / Fatigued / Very Fatigued)
  ```

---

### 5. ❤️ Remote Heart Rate (rPPG) — NEW

| Aspect | Details |
|--------|---------|
| **Technology** | Remote Photoplethysmography (rPPG) |
| **Architecture** | MTTS-CAN or PhysNet |
| **Input** | Webcam video (RGB skin pixel analysis) |
| **Output** | Heart rate (BPM), Heart Rate Variability (HRV) |
| **Accuracy** | ±3-5 BPM in controlled lighting |

#### Recommended: **MTTS-CAN (Multi-Task Temporal Shift Convolutional Attention Network)**

- **Why add rPPG?**
  - Non-contact heart rate measurement from webcam
  - Provides physiological stress signal (not just facial expression)
  - HRV analysis is a validated clinical stress indicator
  - No additional hardware required

- **Do we need to train our own?** ❌ **NO — Use pre-trained**
  - Use `rPPG-Toolbox` (open-source, well-maintained)
  - MTTS-CAN comes with pre-trained weights
  - Integrates with existing MediaPipe face detection pipeline

- **Implementation via:** `pyVHR` or `rPPG-Toolbox`

---

### 6. 🔗 Multi-Modal Fusion Engine

All individual model outputs are fused into a **unified clinical assessment**:

```
┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Emotion      │  │ Respiratory  │  │ Pain         │  │ Fatigue      │  │ Heart Rate   │
│ Score        │  │ Event        │  │ Intensity    │  │ PERCLOS      │  │ BPM + HRV    │
│ (0-1)        │  │ (class+conf) │  │ (0-10)       │  │ (0-100%)     │  │              │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                 │                 │                 │                 │
       └─────────────────┴─────────────────┴─────────────────┴─────────────────┘
                                           │
                               ┌───────────▼───────────┐
                               │   FUSION ENGINE       │
                               │   (XGBoost or         │
                               │    Attention-based     │
                               │    Neural Network)     │
                               └───────────┬───────────┘
                                           │
                               ┌───────────▼───────────┐
                               │  CLINICAL OUTPUT      │
                               │  • Overall Risk Score │
                               │  • Stress Level       │
                               │  • Alert Priority     │
                               │  • Confidence Band    │
                               └───────────────────────┘
```

- **Do we need to train our own?** ✅ **YES**
  - Train XGBoost/LightGBM fusion model on combined features
  - Alternative: Attention-based neural network for learned feature importance
  - Requires labeled clinical data (can start with synthetic/rule-based labels)

---

## 🏛️ Clean Architecture — Project Structure

```
medwatch/
│
├── README.md
├── docker-compose.yml                    # Full stack orchestration
├── .env.example                          # Environment variables template
├── Makefile                              # Common commands
│
├── backend/                              # Python Backend (FastAPI)
│   ├── pyproject.toml                    # Dependencies (Poetry/uv)
│   ├── alembic/                          # Database migrations
│   │   ├── alembic.ini
│   │   └── versions/
│   │
│   ├── src/
│   │   ├── __init__.py
│   │   ├── main.py                       # FastAPI app entry point
│   │   │
│   │   ├── core/                         # ⚙️ SHARED UTILITIES
│   │   │   ├── config.py                 # Settings (Pydantic BaseSettings)
│   │   │   ├── security.py               # JWT, password hashing
│   │   │   ├── exceptions.py             # Global exception handlers
│   │   │   ├── logging.py                # Structured logging
│   │   │   └── events.py                 # Application event bus
│   │   │
│   │   ├── domain/                       # 🧠 DOMAIN LAYER (Pure Python — NO framework imports)
│   │   │   ├── __init__.py
│   │   │   │
│   │   │   ├── patient/
│   │   │   │   ├── entities.py           # Patient, PatientProfile
│   │   │   │   ├── value_objects.py      # PatientId, MedicalRecordNumber
│   │   │   │   └── errors.py            # PatientNotFoundError
│   │   │   │
│   │   │   ├── session/
│   │   │   │   ├── entities.py           # ConsultationSession, SessionStatus
│   │   │   │   ├── value_objects.py      # SessionId, Duration, TimeRange
│   │   │   │   └── errors.py            # SessionExpiredError
│   │   │   │
│   │   │   ├── analysis/
│   │   │   │   ├── entities.py           # AnalysisResult, ClinicalAssessment
│   │   │   │   ├── value_objects.py      # EmotionScore, StressLevel, PainLevel
│   │   │   │   │                         # RespiratoryEvent, FatigueScore
│   │   │   │   │                         # HeartRateReading, RiskScore
│   │   │   │   └── events.py            # CoughDetected, FatigueAlert
│   │   │   │                             # HighStressDetected, PainDetected
│   │   │   │
│   │   │   └── ports/                    # 🔌 PORT INTERFACES (Abstract)
│   │   │       ├── repositories.py       # IPatientRepository, ISessionRepository
│   │   │       ├── ai_services.py        # IEmotionAnalyzer, IRespiratoryAnalyzer
│   │   │       │                         # IPainDetector, IFatigueDetector
│   │   │       │                         # IHeartRateEstimator, IFusionEngine
│   │   │       ├── streaming.py          # IStreamingService
│   │   │       └── notification.py       # IAlertNotifier
│   │   │
│   │   ├── application/                  # 📋 APPLICATION LAYER (Use Cases)
│   │   │   ├── __init__.py
│   │   │   │
│   │   │   ├── session/
│   │   │   │   ├── start_session.py      # StartConsultationUseCase
│   │   │   │   ├── end_session.py        # EndConsultationUseCase
│   │   │   │   └── get_session.py        # GetSessionDetailsUseCase
│   │   │   │
│   │   │   ├── analysis/
│   │   │   │   ├── process_frame.py      # ProcessVideoFrameUseCase
│   │   │   │   ├── process_audio.py      # ProcessAudioChunkUseCase
│   │   │   │   └── get_assessment.py     # GetClinicalAssessmentUseCase
│   │   │   │
│   │   │   ├── patient/
│   │   │   │   ├── register_patient.py   # RegisterPatientUseCase
│   │   │   │   └── get_history.py        # GetPatientHistoryUseCase
│   │   │   │
│   │   │   └── report/
│   │   │       └── generate_report.py    # GenerateSessionReportUseCase
│   │   │
│   │   ├── infrastructure/               # 🔧 INFRASTRUCTURE LAYER (Adapters)
│   │   │   ├── __init__.py
│   │   │   │
│   │   │   ├── ai/                       # AI Model Implementations
│   │   │   │   ├── emotion_analyzer.py   # ViT + AffectNet+ adapter
│   │   │   │   ├── respiratory_analyzer.py # BEATs/AST + ICBHI adapter
│   │   │   │   ├── pain_detector.py      # ConvNeXt + LSTM adapter
│   │   │   │   ├── fatigue_detector.py   # YOLOv8 + PERCLOS adapter
│   │   │   │   ├── heart_rate_estimator.py # MTTS-CAN / rPPG adapter
│   │   │   │   ├── fusion_engine.py      # Multi-modal fusion adapter
│   │   │   │   ├── temporal_smoother.py  # Kalman filter + sliding window
│   │   │   │   └── audio_enhancer.py     # CMGAN noise reduction
│   │   │   │
│   │   │   ├── db/                       # Database
│   │   │   │   ├── models.py             # SQLAlchemy ORM models
│   │   │   │   ├── session_repo.py       # SQLAlchemy session repository
│   │   │   │   ├── patient_repo.py       # SQLAlchemy patient repository
│   │   │   │   └── connection.py         # Database connection pool
│   │   │   │
│   │   │   ├── streaming/                # Real-time Streaming
│   │   │   │   ├── livekit_service.py    # LiveKit WebRTC integration
│   │   │   │   ├── livekit_agent.py      # AI Agent (joins call as participant)
│   │   │   │   └── websocket_handler.py  # FastAPI WebSocket for dashboard updates
│   │   │   │
│   │   │   ├── auth/                     # Authentication
│   │   │   │   ├── jwt_handler.py        # JWT token management
│   │   │   │   └── oauth_provider.py     # OAuth2 integration
│   │   │   │
│   │   │   └── storage/                  # File Storage
│   │   │       └── session_storage.py    # Session recordings storage
│   │   │
│   │   └── api/                          # 🌐 PRESENTATION LAYER (FastAPI Routes)
│   │       ├── __init__.py
│   │       ├── deps.py                   # Dependency injection
│   │       │
│   │       └── v1/
│   │           ├── auth.py               # POST /auth/login, /auth/register
│   │           ├── patients.py           # CRUD /patients
│   │           ├── sessions.py           # /sessions/start, /sessions/end
│   │           ├── analysis.py           # /analysis/frame, /analysis/audio
│   │           ├── reports.py            # /reports/generate, /reports/{id}
│   │           └── streaming.py          # /ws/dashboard, /streaming/token
│   │
│   ├── models/                           # 🧪 Trained Model Weights
│   │   ├── respiratory/
│   │   │   └── beats_icbhi_finetuned.pt
│   │   ├── emotion/
│   │   │   └── vit_affectnet_plus.pt
│   │   ├── pain/
│   │   │   └── convnext_lstm_pain.pt
│   │   ├── fatigue/
│   │   │   └── pfld_landmarks.pt
│   │   ├── rppg/
│   │   │   └── mtts_can_weights.pt
│   │   └── fusion/
│   │       └── xgboost_fusion.pkl
│   │
│   └── tests/
│       ├── unit/
│       │   ├── domain/                   # Test pure domain logic
│       │   └── application/              # Test use cases with fakes
│       ├── integration/
│       │   ├── ai/                       # Test model accuracy
│       │   └── db/                       # Test database operations
│       └── e2e/
│           └── test_consultation_flow.py
│
├── frontend/                             # React Frontend (Next.js)
│   ├── package.json
│   ├── next.config.js
│   │
│   ├── src/
│   │   ├── app/                          # Next.js App Router
│   │   │   ├── layout.tsx                # Root layout
│   │   │   ├── page.tsx                  # Landing page
│   │   │   ├── login/
│   │   │   ├── dashboard/                # Main monitoring dashboard
│   │   │   ├── consultation/             # Live video call page
│   │   │   ├── patients/                 # Patient management
│   │   │   ├── reports/                  # Session reports
│   │   │   └── settings/                 # User settings
│   │   │
│   │   ├── components/
│   │   │   ├── ui/                       # Base UI components (shadcn/ui)
│   │   │   ├── video/
│   │   │   │   ├── VideoCall.tsx          # LiveKit video room
│   │   │   │   └── VideoOverlay.tsx       # AI analysis overlays
│   │   │   ├── dashboard/
│   │   │   │   ├── EmotionPanel.tsx       # Real-time emotion display
│   │   │   │   ├── RespiratoryPanel.tsx   # Respiratory events
│   │   │   │   ├── FatiguePanel.tsx       # Fatigue metrics
│   │   │   │   ├── VitalsPanel.tsx        # Heart rate, HRV
│   │   │   │   ├── PainPanel.tsx          # Pain detection
│   │   │   │   ├── StressTimeline.tsx     # Stress over time (Canvas chart)
│   │   │   │   ├── EventTimeline.tsx      # Clinical events feed
│   │   │   │   └── RiskIndicator.tsx      # Overall risk score
│   │   │   ├── session/
│   │   │   │   ├── SessionControls.tsx    # Start/stop/pause
│   │   │   │   └── SessionSummary.tsx     # End-of-session report
│   │   │   └── patient/
│   │   │       ├── PatientCard.tsx
│   │   │       └── PatientHistory.tsx
│   │   │
│   │   ├── hooks/
│   │   │   ├── useWebSocket.ts           # WebSocket connection
│   │   │   ├── useLiveKit.ts             # LiveKit room management
│   │   │   ├── useAnalysis.ts            # Analysis state management
│   │   │   └── useSession.ts             # Session lifecycle
│   │   │
│   │   ├── lib/
│   │   │   ├── api.ts                    # API client
│   │   │   ├── auth.ts                   # Auth utilities
│   │   │   └── constants.ts              # App constants
│   │   │
│   │   ├── stores/                       # State management (Zustand)
│   │   │   ├── sessionStore.ts
│   │   │   ├── analysisStore.ts
│   │   │   └── authStore.ts
│   │   │
│   │   └── i18n/                         # Internationalization
│   │       ├── en.json
│   │       └── fr.json
│   │
│   └── public/
│       └── assets/
│
├── ai-training/                          # 🧪 Model Training Scripts
│   ├── respiratory/
│   │   ├── train_beats_icbhi.py          # Fine-tune BEATs on ICBHI
│   │   ├── evaluate.py                   # Model evaluation
│   │   └── data/                         # ICBHI dataset
│   ├── pain/
│   │   ├── train_convnext_pain.py        # Train pain detection
│   │   └── data/                         # UNBC-McMaster dataset
│   ├── fusion/
│   │   ├── train_fusion.py              # Train fusion engine
│   │   └── data/
│   └── notebooks/                        # Jupyter notebooks for experimentation
│       ├── respiratory_analysis.ipynb
│       ├── emotion_benchmarks.ipynb
│       └── fusion_experiments.ipynb
│
└── infra/                                # 🐳 Infrastructure
    ├── docker/
    │   ├── backend.Dockerfile
    │   ├── frontend.Dockerfile
    │   └── livekit.Dockerfile
    ├── nginx/
    │   └── nginx.conf                    # Reverse proxy config
    └── k8s/                              # Kubernetes manifests (production)
        ├── deployment.yaml
        └── service.yaml
```

---

## 📡 Live Streaming Architecture

### Why LiveKit + WebRTC?

| Feature | Current (HTTP Polling) | New (LiveKit + WebRTC) |
|---------|----------------------|----------------------|
| **Latency** | ~3000ms (3s polling interval) | **<200ms** (real-time) |
| **Bandwidth** | High (base64 encoded frames) | **Low** (VP8/VP9 compressed) |
| **Audio/Video Sync** | Not synced | **Native sync** |
| **Multi-party** | Not supported | **Doctor + Patient + AI Agent** |
| **Recording** | None | **Built-in recording** |

### Streaming Data Flow

```
┌────────────┐                   ┌────────────────┐                  ┌─────────────┐
│  PATIENT   │◄── WebRTC/SFU ──►│   LIVEKIT      │◄── WebRTC ─────►│   DOCTOR    │
│  Browser   │                   │   SERVER       │                  │   Browser   │
└──────┬─────┘                   └───────┬────────┘                  └──────┬──────┘
       │                                 │                                  │
       │                                 │ Media Tracks                     │
       │                                 ▼                                  │
       │                   ┌─────────────────────────┐                      │
       │                   │     AI AGENT            │                      │
       │                   │  (LiveKit Python SDK)   │                      │
       │                   │                         │                      │
       │                   │  Subscribes to:         │                      │
       │                   │  • Patient video track  │                      │
       │                   │  • Patient audio track  │                      │
       │                   │                         │                      │
       │                   │  Processes via:         │                      │
       │                   │  • Emotion (ViT)        │                      │
       │                   │  • Respiratory (BEATs)  │                      │
       │                   │  • Pain (ConvNeXt)      │                      │
       │                   │  • Fatigue (PERCLOS)    │                      │
       │                   │  • Heart Rate (rPPG)    │                      │
       │                   │  • Fusion Engine        │                      │
       │                   └──────────┬──────────────┘                      │
       │                              │                                     │
       │                    WebSocket (results)                             │
       │                              │                                     │
       │                              ▼                                     │
       │                   ┌──────────────────────┐                         │
       │                   │   FASTAPI BACKEND    │─── WebSocket ──────────►│
       │                   │   (Dashboard Data)   │   (real-time updates)   │
       │                   └──────────────────────┘                         │
```

### LiveKit AI Agent Architecture

The AI agent joins the LiveKit room as a **silent participant** that:
1. **Subscribes** to the patient's video and audio tracks
2. **Samples video frames** at configurable intervals (e.g., every 500ms for emotion, every 140ms for landmarks)
3. **Buffers audio** into configurable windows (e.g., 10-second chunks for respiratory analysis)
4. **Publishes results** via WebSocket data channel to the doctor's dashboard
5. **Records** the session for compliance and later review

---

## 🗄️ Database Design

### Technology: **PostgreSQL + Redis**

- **PostgreSQL**: Primary data store (patients, sessions, analysis results, reports)
- **Redis**: Real-time cache (current session state, WebSocket pub/sub, model inference cache)

### Core Schema

```sql
-- Patients
CREATE TABLE patients (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    first_name      VARCHAR(100) NOT NULL,
    last_name       VARCHAR(100) NOT NULL,
    date_of_birth   DATE,
    medical_id      VARCHAR(50) UNIQUE,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Consultation Sessions
CREATE TABLE sessions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id      UUID REFERENCES patients(id),
    doctor_id       UUID REFERENCES users(id),
    status          VARCHAR(20) DEFAULT 'active',    -- active, paused, completed
    started_at      TIMESTAMPTZ DEFAULT NOW(),
    ended_at        TIMESTAMPTZ,
    duration_seconds INTEGER,
    livekit_room_id VARCHAR(100),
    recording_url   TEXT
);

-- Analysis Snapshots (time-series)
CREATE TABLE analysis_snapshots (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id      UUID REFERENCES sessions(id),
    timestamp       TIMESTAMPTZ DEFAULT NOW(),
    
    -- Emotion
    emotion         VARCHAR(20),
    emotion_confidence FLOAT,
    stress_score    FLOAT,
    
    -- Respiratory
    respiratory_event VARCHAR(20),
    respiratory_confidence FLOAT,
    
    -- Pain
    pain_detected   BOOLEAN DEFAULT FALSE,
    pain_intensity  FLOAT,
    
    -- Fatigue
    perclos_score   FLOAT,
    blink_rate      FLOAT,
    yawn_count      INTEGER,
    fatigue_level   VARCHAR(20),
    
    -- Vitals
    heart_rate_bpm  FLOAT,
    hrv_score       FLOAT,
    
    -- Fusion
    overall_risk_score FLOAT,
    risk_level      VARCHAR(20),
    confidence_band FLOAT
);

-- Clinical Events (significant moments)
CREATE TABLE clinical_events (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id      UUID REFERENCES sessions(id),
    timestamp       TIMESTAMPTZ DEFAULT NOW(),
    event_type      VARCHAR(50),     -- cough, wheeze, high_stress, fatigue_alert, pain_spike
    severity        VARCHAR(20),     -- low, medium, high, critical
    description     TEXT,
    metadata        JSONB
);

-- Session Reports
CREATE TABLE session_reports (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id      UUID REFERENCES sessions(id),
    generated_at    TIMESTAMPTZ DEFAULT NOW(),
    summary         TEXT,
    recommendations TEXT,
    risk_assessment JSONB,
    report_pdf_url  TEXT
);
```

---

## 🛠️ Technology Stack Summary

### Backend

| Component | Technology | Why |
|-----------|-----------|-----|
| **Framework** | FastAPI | Async, fast, auto-docs, dependency injection |
| **Language** | Python 3.11+ | AI/ML ecosystem |
| **ORM** | SQLAlchemy 2.0 | Async support, mature |
| **Migrations** | Alembic | Industry standard |
| **Validation** | Pydantic v2 | Fast, type-safe |
| **Task Queue** | Celery + Redis | Background model training, report generation |
| **WebSocket** | FastAPI WebSockets | Native async support |
| **Auth** | JWT + OAuth2 | Stateless, scalable |
| **Logging** | structlog | Structured JSON logging |
| **Testing** | pytest + httpx | Async test support |

### Frontend

| Component | Technology | Why |
|-----------|-----------|-----|
| **Framework** | Next.js 14+ (App Router) | SSR, routing, API routes |
| **Language** | TypeScript | Type safety |
| **UI Library** | shadcn/ui + Radix | Accessible, customizable |
| **Styling** | Tailwind CSS | Rapid UI development |
| **State** | Zustand | Lightweight, performant |
| **Charts** | Canvas API + Recharts | Real-time rendering |
| **Video** | LiveKit React SDK | Native WebRTC components |
| **i18n** | next-intl | Built-in Next.js support |
| **Forms** | React Hook Form + Zod | Validation |

### AI / ML

| Component | Technology | Why |
|-----------|-----------|-----|
| **Deep Learning** | PyTorch | Industry standard, HuggingFace ecosystem |
| **Model Hub** | HuggingFace Transformers | Pre-trained models, easy fine-tuning |
| **Audio Processing** | torchaudio + librosa | Medical-grade audio features |
| **Face Detection** | MediaPipe + YOLOv8 | Robust, fast |
| **rPPG** | rPPG-Toolbox / pyVHR | Pre-built pipeline |
| **Fusion** | XGBoost / scikit-learn | Proven for tabular fusion |
| **Serving** | ONNX Runtime | Optimized inference |

### Infrastructure

| Component | Technology | Why |
|-----------|-----------|-----|
| **Containers** | Docker + Docker Compose | Consistent environments |
| **WebRTC** | LiveKit (self-hosted or cloud) | Production WebRTC |
| **Database** | PostgreSQL 16 | Reliable, JSON support |
| **Cache** | Redis 7 | Real-time pub/sub |
| **Reverse Proxy** | Nginx | SSL termination, load balancing |
| **CI/CD** | GitHub Actions | Automated testing + deployment |

---

## 📊 Model Decision Matrix

| Model | Pretrained Available? | Need Fine-tuning? | Training Data | Estimated Effort | Expected Accuracy |
|-------|----------------------|-------------------|---------------|------------------|-------------------|
| **BEATs (Respiratory)** | ✅ Yes (AudioSet) | ✅ Yes (on ICBHI) | ICBHI 2017 (920 recordings) | 2-3 weeks | ~87-90% |
| **ViT (Emotion)** | ✅ Yes (AffectNet+) | ⚠️ Optional | AffectNet+ (400K+ images) | 0-1 week | ~80-88% |
| **ConvNeXt+LSTM (Pain)** | ✅ Partial (ImageNet) | ✅ Yes | UNBC-McMaster | 2-3 weeks | ~75-85% |
| **YOLOv8 (Face Detect)** | ✅ Yes | ❌ No | WIDER FACE | 0 days | ~95%+ |
| **PFLD (Landmarks)** | ✅ Yes | ❌ No | 300W/WFLW | 0 days | ~95%+ |
| **MTTS-CAN (rPPG)** | ✅ Yes | ❌ No | UBFC-rPPG | 0 days | ±3-5 BPM |
| **XGBoost (Fusion)** | ❌ No | ✅ Yes (from scratch) | Combined features | 1-2 weeks | Depends on data |

---

## 🗓️ Implementation Phases

### Phase 1: Foundation (Weeks 1-2)
- [ ] Set up project structure (Clean Architecture)
- [ ] Configure Docker, PostgreSQL, Redis
- [ ] Implement domain entities and value objects
- [ ] Set up FastAPI with auth (JWT)
- [ ] Initialize Next.js frontend with base layout
- [ ] Set up LiveKit server (Docker)

### Phase 2: Core AI Pipeline (Weeks 3-5)
- [ ] Integrate ViT emotion model (pre-trained, no fine-tuning needed initially)
- [ ] Fine-tune BEATs on ICBHI for respiratory classification
- [ ] Implement MediaPipe + PERCLOS fatigue detection
- [ ] Integrate MTTS-CAN for rPPG heart rate
- [ ] Build temporal smoothing layer (Kalman filter)

### Phase 3: Live Streaming (Weeks 5-6)
- [ ] Implement LiveKit AI Agent (joins room, subscribes to tracks)
- [ ] Build WebSocket dashboard updates
- [ ] Create video call UI (LiveKit React SDK)
- [ ] Implement session recording

### Phase 4: Frontend Dashboard (Weeks 6-8)
- [ ] Build all dashboard panels (emotion, respiratory, fatigue, vitals, pain)
- [ ] Implement real-time charts (Canvas/Recharts)
- [ ] Build session management flow
- [ ] Add patient management pages
- [ ] Implement report generation

### Phase 5: Advanced AI (Weeks 8-10)
- [ ] Train pain detection model (ConvNeXt + LSTM)
- [ ] Build multi-modal fusion engine
- [ ] Add audio enhancement preprocessing (noise reduction)
- [ ] Implement clinical event detection and alerting

### Phase 6: Polish & Validation (Weeks 10-12)
- [ ] End-to-end testing
- [ ] Performance optimization (ONNX Runtime)
- [ ] Security hardening
- [ ] i18n (English + French)
- [ ] Clinical validation setup
- [ ] Documentation

---

## ⚡ Key Architectural Decisions

### 1. Why FastAPI over Flask?
- Native async support (critical for WebSocket + streaming)
- Built-in dependency injection (perfect for Clean Architecture)
- Auto-generated OpenAPI docs
- 5-10x faster than Flask for concurrent requests
- Native Pydantic validation

### 2. Why LiveKit over raw WebRTC?
- WebRTC is incredibly complex to implement from scratch (~6 months of work)
- LiveKit handles ICE, STUN/TURN, SFU, media routing
- Python Agents SDK allows AI to join calls as participants
- Built-in recording and room management
- Free self-hosted option available

### 3. Why PyTorch over TensorFlow?
- Dominant in research (all latest medical models use PyTorch)
- HuggingFace ecosystem is PyTorch-first
- Better debugging experience
- ONNX export for production optimization

### 4. Why Next.js over vanilla HTML?
- Component-based architecture (reusable dashboard panels)
- Server-side rendering for initial load performance
- Built-in routing, API routes, and middleware
- TypeScript support for large codebase
- Massive ecosystem (shadcn/ui, LiveKit SDK)

### 5. Why PostgreSQL over SQLite/MongoDB?
- Time-series analysis queries (for historical data)
- JSONB support for flexible metadata
- Concurrent read/write (multiple sessions simultaneously)
- Alembic migrations for schema evolution
- Production-ready replication and backup

---

## 🔐 Security Considerations

- **Authentication:** JWT tokens with short expiry + refresh tokens
- **Authorization:** Role-based access (Doctor, Admin, Viewer)
- **Transport:** All WebSocket and API traffic over TLS/SSL
- **WebRTC:** DTLS-SRTP encryption (handled by LiveKit)
- **Data at rest:** PostgreSQL encryption, encrypted file storage
- **HIPAA readiness:** Audit logging, data retention policies, BAA-ready infrastructure
- **On-device inference:** Models run server-side (no patient data sent to external APIs)

---

## 📚 References

### Models & Datasets
- **BEATs:** https://github.com/microsoft/unilm/tree/master/beats
- **ICBHI 2017:** https://www.kaggle.com/vbookshelf/respiratory-sound-database
- **AffectNet+:** https://huggingface.co/datasets
- **UNBC-McMaster Pain:** https://www.pitt.edu/~jeffcohn/PainDatabase.html
- **rPPG-Toolbox:** https://github.com/ubicomplab/rPPG-Toolbox
- **MediaPipe:** https://mediapipe.dev/

### Frameworks
- **LiveKit:** https://livekit.io/
- **FastAPI:** https://fastapi.tiangolo.com/
- **Next.js:** https://nextjs.org/
- **shadcn/ui:** https://ui.shadcn.com/
- **HuggingFace Transformers:** https://huggingface.co/docs/transformers

---

> **Next Step:** Review this plan, ask questions or request changes, then we begin implementation starting with Phase 1 — the Clean Architecture foundation.
