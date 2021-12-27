from abc import ABC, abstractmethod
import numpy as np


class ComponentRenderer(ABC):

    @abstractmethod
    def render(self, start: int, samples: int) -> np.ndarray:
        raise NotImplementedError()

    @property
    def sample_rate(self) -> int:
        return 44100

    def sample_to_time(self, sample: int) -> float:
        return sample / self.sample_rate

    def sample_range_to_times(self, start: int, samples: int) -> np.ndarray:
        return np.arange(start, start + samples) / self.sample_rate
