from typing import Dict, Any
from modules.base import BaseAnalyzer
from modules.fusion.fusion_engine import MultiModalFusionEngine
from core.config import settings

class FusionAnalyzer(BaseAnalyzer):
    """
    Unified Multi-Modal Fusion Analyzer.
    """

    def __init__(self):
        super().__init__(name="FusionAnalyzer")
        self.engine = MultiModalFusionEngine(model_path=settings.FUSION_MODEL_PATH)

    def load_model(self) -> bool:
        self._is_loaded = self.engine.load()
        return self._is_loaded

    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Input data dict contains:
        - 'respiratory': dict result from RespiratoryAnalyzer
        - 'emotion': dict result from EmotionAnalyzer
        - 'fatigue': dict result from FatigueAnalyzer
        """
        resp_data = data.get("respiratory", {})
        emo_data = data.get("emotion", {})
        fatigue_data = data.get("fatigue", {})

        return self.engine.fuse(
            respiratory_data=resp_data,
            emotion_data=emo_data,
            fatigue_data=fatigue_data
        )
