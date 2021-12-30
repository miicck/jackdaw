from jackdaw.Data.ProjectData import RouterComponentData
from jackdaw.UI.RouterComponent import RouterComponent
from jackdaw.Rendering.ComponentRenderer import ComponentRenderer
from jackdaw.Gi import Gtk
from typing import Union, Dict
import numpy as np


class StereoToMono(RouterComponent):

    def __init__(self, id: int):
        super().__init__(id)
        self.add_input_node("In")
        self.add_output_node("Left")
        self.add_output_node("Right")
        self.content = Gtk.Label(label="Stereo\nTo\nMono")


class StereoToMonoRenderer(ComponentRenderer):

    def render_output_signal(self, node: str, channel: int, start: int, samples: int) -> Union[np.ndarray, None]:
        raise NotImplementedError()

    def render(self, output_node: str, channel: int,
               input_node_signals: Dict[str, Dict[int, np.ndarray]]) -> Dict[int, np.ndarray]:
        raise NotImplementedError()


class StereoToMonoData(RouterComponentData):

    def create_component_renderer(self):
        return StereoToMonoRenderer()

    def create_component(self, id: int):
        return StereoToMono(id)
