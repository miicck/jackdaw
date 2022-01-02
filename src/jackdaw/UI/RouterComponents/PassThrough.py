from jackdaw.Data.ProjectData import RouterComponentData
from jackdaw.UI.RouterComponent import RouterComponent
from jackdaw.Rendering.ComponentRenderer import ComponentRenderer
from jackdaw.Gi import Gtk
from typing import Union, Dict
import numpy as np
from jackdaw.Rendering.Signal import Signal


class PassThroughData(RouterComponentData):

    def create_component(self, id: int):
        return PassThrough(id)

    def create_component_renderer(self):
        return PassThroughRenderer()


class PassThroughRenderer(ComponentRenderer):

    def render(self, output_node: str, channel: int, inputs: Dict[str, Signal]) -> Signal:
        if "In" in inputs:
            return inputs["In"]
        return Signal()


class PassThrough(RouterComponent):

    def __init__(self, id: int):
        super().__init__(id)
        self.add_input_node("In")
        self.add_output_node("Out")
        self.content = Gtk.Label(label="Pass through")
