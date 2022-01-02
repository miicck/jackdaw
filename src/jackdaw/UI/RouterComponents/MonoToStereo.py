from jackdaw.Data.ProjectData import RouterComponentData
from jackdaw.UI.RouterComponent import RouterComponent
from jackdaw.Rendering.ComponentRenderer import ComponentRenderer
from jackdaw.Gi import Gtk
from typing import Dict
from jackdaw.Rendering.Signal import Signal


class MonoToStereo(RouterComponent):

    def __init__(self, id: int):
        super().__init__(id)
        self.add_input_node("Left")
        self.add_input_node("Right")
        self.add_output_node("Out")
        self.content = Gtk.Label(label="Mono\nTo\nStereo")


class MonoToStereoRenderer(ComponentRenderer):

    def render(self, output_node: str, channel: int, inputs: Dict[str, Signal]) -> Signal:
        result = Signal()
        if "Left" in inputs:
            result[0] = inputs["Left"][0]
        if "Right" in inputs:
            result[1] = inputs["Right"][0]
        return result


class MonoToStereoData(RouterComponentData):

    def create_component_renderer(self):
        return MonoToStereoRenderer()

    def create_component(self, id: int):
        return MonoToStereo(id)
