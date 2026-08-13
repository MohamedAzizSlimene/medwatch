import json
import time
import base64
import numpy as np
import cv2
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from core.logging import logger
from modules.respiratory import RespiratoryAnalyzer
from modules.emotion import EmotionAnalyzer
from modules.fatigue import FatigueAnalyzer
from modules.fusion import FusionAnalyzer

router = APIRouter()

# ── Instantiate AI Analyzers ────────────────────────────────────────────────
respiratory_analyzer = RespiratoryAnalyzer()
emotion_analyzer = EmotionAnalyzer()
fatigue_analyzer = FatigueAnalyzer()
fusion_analyzer = FusionAnalyzer()


def _load_all_models():
    """Load all 4 AI module models at server startup."""
    logger.info("==================================================")
    logger.info("Initializing MedWatch AI Engines...")
    respiratory_analyzer.load_model()
    emotion_analyzer.load_model()
    fatigue_analyzer.load_model()
    fusion_analyzer.load_model()
    logger.info("All AI models loaded successfully. Ready for incoming streams.")
    logger.info("==================================================")


# Call on import (FastAPI startup)
_load_all_models()


# ── Connection Manager ───────────────────────────────────────────────────────
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"🟢 [WS] Client connected. Total active sessions: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"🔴 [WS] Client disconnected. Active sessions: {len(self.active_connections)}")

    async def send_json(self, websocket: WebSocket, data: dict):
        await websocket.send_json(data)


manager = ConnectionManager()


# ── Frame & Audio Decoding Helpers ───────────────────────────────────────────
def decode_frame(frame_b64: str) -> np.ndarray | None:
    try:
        img_bytes = base64.b64decode(frame_b64)
        arr = np.frombuffer(img_bytes, dtype=np.uint8)
        frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)  # BGR
        return frame
    except Exception as e:
        logger.warning(f"Frame decode error: {e}")
        return None


def decode_audio(audio_b64: str) -> np.ndarray | None:
    try:
        audio_bytes = base64.b64decode(audio_b64)
        audio_array = np.frombuffer(audio_bytes, dtype=np.float32)
        return audio_array
    except Exception as e:
        logger.warning(f"Audio decode error: {e}")
        return None


# ── WebSocket Endpoint ────────────────────────────────────────────────────────
@router.websocket("/ws/stream")
async def websocket_stream_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    frame_counter = 0
    
    # State history to detect state transitions for explicit logging
    last_hand_active = False
    last_yawn_active = False

    try:
        while True:
            raw_data = await websocket.receive_text()

            try:
                payload = json.loads(raw_data)
            except json.JSONDecodeError:
                await manager.send_json(websocket, {"error": "Invalid JSON payload"})
                continue

            timestamp = time.time()
            frame_counter += 1

            # ── Decode Inputs ─────────────────────────────────────────────
            frame = None
            if "frame_b64" in payload and payload["frame_b64"]:
                frame = decode_frame(payload["frame_b64"])

            audio_data = None
            if "audio_b64" in payload and payload["audio_b64"]:
                audio_data = decode_audio(payload["audio_b64"])

            nose_coords = payload.get("nose_coords")
            wrist_coords = payload.get("wrist_coords")

            # ── 1. Run Fatigue Analysis First (Extracts Face Box in single pass) ──
            fatigue_res = fatigue_analyzer.analyze({"frame": frame})
            face_bbox = fatigue_res.get("face_bbox")

            # ── 2. Run Emotion Analysis ───────────────────────────────────
            emotion_res = emotion_analyzer.analyze({"frame": frame})

            # ── 3. Run Respiratory Analysis ───────────────────────────────
            respiratory_res = respiratory_analyzer.analyze({
                "audio_chunk": audio_data,
                "frame": frame,
                "face_bbox": face_bbox,
                "nose_coords": nose_coords,
                "wrist_coords": wrist_coords
            })

            # ── 4. Run Multi-Modal Risk Fusion ─────────────────────────────
            fusion_res = fusion_analyzer.analyze({
                "respiratory": respiratory_res,
                "emotion": emotion_res,
                "fatigue": fatigue_res
            })

            # ── Event Logging for State Transitions & Triggers ─────────────
            hand_active = respiratory_res.get("hand_to_nose_active", False)
            hand_count = respiratory_res.get("hand_to_nose_count", 0)

            if hand_active and not last_hand_active:
                logger.info(f"🖐️ [HAND-TO-NOSE GESTURE DETECTED] Triggered! Total Count: #{hand_count}")
            last_hand_active = hand_active

            is_yawning = fatigue_res.get("is_yawning_now", False)
            mar_score = fatigue_res.get("mar", 0.0)
            yawn_count = fatigue_res.get("yawn_count", 0)
            fatigue_status = fatigue_res.get("status", "NORMAL")

            if is_yawning and not last_yawn_active:
                logger.info(f"🥱 [YAWN DETECTED] Mouth Ratio (MAR): {mar_score} | Total Yawns: #{yawn_count} | Status: {fatigue_status}")
            last_yawn_active = is_yawning

            if respiratory_res.get("respiratory_event") != "normal":
                logger.info(
                    f"🎤 [AUDIO EVENT DETECTED] Event: {respiratory_res.get('respiratory_event').upper()} | "
                    f"Conf: {respiratory_res.get('audio_confidence', 0)*100:.1f}%"
                )

            # ── Structured Summary Logging Every 5 Frames ──────────────────
            if frame_counter % 5 == 0:
                hand_str = f"ACTIVE (#{hand_count}) 🚨" if hand_active else f"Inactive (#{hand_count})"
                logger.info(
                    f"Frame #{frame_counter} | "
                    f"Emotion: {emotion_res.get('dominant_emotion')} ({emotion_res.get('confidence', 0)*100:.0f}%) | "
                    f"Fatigue: {fatigue_status} (Yawns: {yawn_count}, MAR: {mar_score}) | "
                    f"Hand-to-Nose: {hand_str} | "
                    f"Risk: {fusion_res.get('risk_level')} ({fusion_res.get('overall_risk_score', 0)*100:.0f}%)"
                )

            # ── Send Result Payload Back to Client ─────────────────────────
            result_payload = {
                "timestamp": timestamp,
                "respiratory": respiratory_res,
                "emotion": emotion_res,
                "fatigue": fatigue_res,
                "fusion": fusion_res
            }

            await manager.send_json(websocket, result_payload)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket stream error: {e}")
        manager.disconnect(websocket)
