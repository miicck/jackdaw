from abc import ABC, abstractmethod
import numpy
from typing import Dict
from jackdaw.Rendering.Signal import Signal


class ComponentRenderer(ABC):

    @abstractmethod
    def render(self, output_node: str, start: int, samples: int, inputs: Dict[str, Signal]) -> Signal:
        raise NotImplementedError()

    ################
    # TIME/SAMPLES #
    ################

    @property
    def sample_rate(self) -> int:
        return 44100

    def sample_to_time(self, sample: int) -> float:
        return sample / self.sample_rate

    def sample_range_to_times(self, start: int, samples: int) -> numpy.ndarray:
        return numpy.arange(start, start + samples) / self.sample_rate
