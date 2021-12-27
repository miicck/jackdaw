from abc import ABC, abstractmethod
import numpy
from typing import Union, Dict, Tuple, List
from collections import defaultdict


class ComponentRenderer(ABC):

    def __init__(self):
        self._input_renderers: Dict[str, List[Tuple['ComponentRenderer', str]]] = defaultdict(lambda: [])

    @abstractmethod
    def render_output_signal(self, node: str, channel: int, start: int, samples: int) -> Union[numpy.ndarray, None]:
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

    #################
    # INPUT SIGNALS #
    #################

    def connect_input_node(self, renderer: 'ComponentRenderer', out_node: str, in_node: str):
        self._input_renderers[in_node].append((renderer, out_node))

    def clear_input_nodes(self):
        self._input_renderers.clear()

    def render_input_signal(self, node: str, channel: int, start: int, samples: int) -> Union[numpy.ndarray, None]:
        # Node not connected
        if len(self._input_renderers[node]) == 0:
            return None

        # Sum signals from each connected input renderer
        result = None
        for renderer, out_node in self._input_renderers[node]:
            render = renderer.render_output_signal(out_node, channel, start, samples)
            if render is None:
                continue  # Renderer doesn't output this channel

            if result is None:
                result = render  # No result so far, this is the first one
            else:
                result += render  # Sum results

        return result
