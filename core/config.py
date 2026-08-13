import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Application Settings for MedWatch AI Microservice
    """
    APP_NAME: str = "MedWatch AI Engine"
    VERSION: str = "1.0.0"
    DEBUG: bool = True

    HOST: str = "0.0.0.0"
    PORT: int = 8000
    LOG_LEVEL: str = "DEBUG"  # Changed to DEBUG for detailed logging

    # Model Weights Paths
    MODEL_DIR: str = "models"

    # Emotion: ViT-Base pre-trained on AffectNet+ (local folder)
    EMOTION_MODEL_PATH: str = "models/emotion/vit_affectnet"

    # Fatigue: YOLOv8 face detector (local .pt file)
    FATIGUE_YOLO_PATH: str = "models/fatigue/yolov8n-face.pt"
    # Fatigue: MediaPipe FaceLandmarker model for geometric MAR / yawn detection
    FATIGUE_FACE_LANDMARKER_PATH: str = "models/fatigue/face_landmarker.task"

    # Respiratory: AST Audio Spectrogram Transformer (local folder)
    RESPIRATORY_AST_MODEL_ID: str = "models/respiratory/ast_audioset"
    RESPIRATORY_AUDIO_SAMPLE_RATE: int = 16000

    # Fusion
    FUSION_MODEL_PATH: str = "models/fusion/xgboost_fusion.pkl"

    # Analysis Thresholds
    PERCLOS_WINDOW_SECONDS: int = 60
    EMOTION_TEMPORAL_WINDOW: int = 3
    CONFIDENCE_THRESHOLD: float = 0.5

    # MediaPipe Face Detection confidence threshold
    FACE_DETECTION_CONFIDENCE: float = 0.5

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
