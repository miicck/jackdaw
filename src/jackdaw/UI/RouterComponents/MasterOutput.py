from jackdaw.Data.ProjectData import RouterComponentData
from jackdaw.UI.RouterComponent import RouterComponent
from jackdaw.Rendering.ComponentRenderer import ComponentRenderer
from jackdaw.Gi import Gtk
from typing import Union
import numpy as np


class MasterOutputData(RouterComponentData):

    def create_component(self, id: int):
        return MasterOutput(id)

    def create_component_renderer(self):
        return MasterOutputRenderer()


class MasterOutputRenderer(ComponentRenderer):

    def render_output_signal(self, node: str, channel: int, start: int, samples: int) -> Union[np.ndarray, None]:
        raise Exception(f"Master output should not be rendered directly, use {self.render_master.__name__} instead")

    def render_master(self, channel: int, start: int, samples: int):
        return self.render_input_signal("To Master", channel, start, samples)


class MasterOutput(RouterComponent):

    def __init__(self, id: int):
        super().__init__(id)
        self.add_input_node("To Master")
        self.content = Gtk.Label(label="Master output")
