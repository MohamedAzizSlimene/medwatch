from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseAnalyzer(ABC):
    """
    Abstract Base Class for all MedWatch AI Modules.
    Ensures a standardized interface across Respiratory, Emotion, Fatigue, and Fusion engines.
    """

    def __init__(self, name: str):
        self.name = name
        self._is_loaded = False

    @abstractmethod
    def load_model(self) -> bool:
        """
        Loads model weights into memory/GPU.
        """
        pass

    @property
    def is_loaded(self) -> bool:
        return self._is_loaded

    @abstractmethod
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Performs inference on input data (frame image, audio array, or combined features).
        Returns a standardized dictionary result.
        """
        pass
