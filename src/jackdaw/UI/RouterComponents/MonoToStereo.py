from jackdaw.Data.ProjectData import RouterComponentData
from jackdaw.UI.RouterComponent import RouterComponent
from jackdaw.Rendering.ComponentRenderer import ComponentRenderer
from jackdaw.Gi import Gtk
from typing import Union
import numpy


class MonoToStereo(RouterComponent):

    def __init__(self, id: int):
        super().__init__(id)
        self.add_input_node("Left")
        self.add_input_node("Right")
        self.add_output_node("Out")
        self.content = Gtk.Label(label="Mono to Stereo")


class MonoToStereoRenderer(ComponentRenderer):

    def render_output_signal(self, node: str, channel: int, start: int, samples: int) -> Union[numpy.ndarray, None]:
        if node != "Out" or channel not in {0, 1}:
            return None

        channel_to_node = {0: "Left", 1: "Right"}
        return self.render_input_signal(channel_to_node[channel], 0, start, samples)


class MonoToSterioData(RouterComponentData):

    def create_component_renderer(self):
        return MonoToStereoRenderer()

    def create_component(self, id: int):
        return MonoToStereo(id)
