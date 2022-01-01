from jackdaw.Data.ProjectData import RouterComponentData
from jackdaw.UI.RouterComponent import RouterComponent
from jackdaw.Rendering.ComponentRenderer import ComponentRenderer
from jackdaw.Gi import Gtk
from typing import Union, Dict
import numpy as np


class MonoToStereo(RouterComponent):

    def __init__(self, id: int):
        super().__init__(id)
        self.add_input_node("Left")
        self.add_input_node("Right")
        self.add_output_node("Out")
        self.content = Gtk.Label(label="Mono\nTo\nStereo")


class MonoToStereoRenderer(ComponentRenderer):

    def render_output_signal(self, node: str, channel: int, start: int, samples: int) -> Union[np.ndarray, None]:
        if node != "Out" or channel not in {0, 1}:
            return None

        channel_to_node = {0: "Left", 1: "Right"}
        return self.render_input_signal(channel_to_node[channel], 0, start, samples)

    def render(self, output_node: str, channel: int,
               input_node_signals: Dict[str, Dict[int, np.ndarray]]) -> Dict[int, np.ndarray]:

        if len(input_node_signals) == 0:
            raise Exception("Tried to render mono to stereo with no inputs!")

        if len(input_node_signals) == 1:
            if "Left" in input_node_signals:
                left = input_node_signals["Left"][0]
                return {
                    0: left,
                    1: np.zeros(len(left))
                }

            if "Right" in input_node_signals:
                right = input_node_signals["Right"][0]
                return {
                    0: np.zeros(len(right)),
                    1: right
                }

        return {
            0: input_node_signals["Left"][0],
            1: input_node_signals["Right"][0]
        }


class MonoToStereoData(RouterComponentData):

    def create_component_renderer(self):
        return MonoToStereoRenderer()

    def create_component(self, id: int):
        return MonoToStereo(id)