from fastapi import APIRouter, status
from core.config import settings
from typing import Dict, Any

router = APIRouter()

@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check() -> Dict[str, Any]:
    """
    Health check diagnostic endpoint.
    """
    return {
        "status": "online",
        "app_name": settings.APP_NAME,
        "version": settings.VERSION,
        "active_modules": [
            "respiratory (audio + visual hand-to-nose)",
            "emotion (ViT + AffectNet+ soft labels)",
            "fatigue (YOLOv8 + PFLD + PERCLOS)",
            "fusion (multi-modal risk score)"
        ]
    }
