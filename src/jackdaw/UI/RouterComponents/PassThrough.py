from jackdaw.Data.ProjectData import RouterComponentData
from jackdaw.UI.RouterComponent import RouterComponent
from jackdaw.Rendering.ComponentRenderer import ComponentRenderer
from jackdaw.Gi import Gtk
from typing import Union, Dict
import numpy as np


class PassThroughData(RouterComponentData):

    def create_component(self, id: int):
        return PassThrough(id)

    def create_component_renderer(self):
        return PassThroughRenderer()


class PassThroughRenderer(ComponentRenderer):

    def render_output_signal(self, node: str, channel: int, start: int, samples: int) -> Union[np.ndarray, None]:
        if node != "Out":
            return None
        return self.render_input_signal("In", channel, start, samples)

    def render(self, output_node: str, channel: int,
               input_node_signals: Dict[str, Dict[int, np.ndarray]]) -> Dict[int, np.ndarray]:
        assert len(input_node_signals) == 1
        assert "In" in input_node_signals
        return input_node_signals["In"]


class PassThrough(RouterComponent):

    def __init__(self, id: int):
        super().__init__(id)
        self.add_input_node("In")
        self.add_output_node("Out")
        self.content = Gtk.Label(label="Pass through")
