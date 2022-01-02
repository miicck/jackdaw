from jackdaw.Data.ProjectData import RouterComponentData
from jackdaw.UI.RouterComponent import RouterComponent
from jackdaw.Rendering.ComponentRenderer import ComponentRenderer
from jackdaw.Gi import Gtk
from typing import Union, Dict
import numpy as np
from jackdaw.Rendering.Signal import Signal


class StereoToMono(RouterComponent):

    def __init__(self, id: int):
        super().__init__(id)
        self.add_input_node("In")
        self.add_output_node("Left")
        self.add_output_node("Right")
        self.content = Gtk.Label(label="Stereo\nTo\nMono")


class StereoToMonoRenderer(ComponentRenderer):

    def render(self, output_node: str, channel: int, inputs: Dict[str, Signal]) -> Signal:
        result = Signal()
        if "In" not in inputs:
            return result

        if output_node == "Left":
            result[0] = inputs["In"][0]
        elif output_node == "Right":
            result[0] = inputs["In"][1]
        return result


class StereoToMonoData(RouterComponentData):

    def create_component_renderer(self):
        return StereoToMonoRenderer()

    def create_component(self, id: int):
        return StereoToMono(id)
