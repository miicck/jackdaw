from jackdaw.Data.ProjectData import RouterComponentData
from jackdaw.UI.RouterComponent import RouterComponent
from jackdaw.Rendering.ComponentRenderer import ComponentRenderer
from jackdaw.Gi import Gtk
import cairo
import numpy as np
from typing import Dict
from jackdaw.Rendering.Signal import Signal


class SineSignalData(RouterComponentData):

    def create_component(self, id: int):
        return SineSignal(id)

    def create_component_renderer(self):
        return SineSignalRenderer()


class SineSignalRenderer(ComponentRenderer):

    def render(self, output_node: str, start: int, samples: int, inputs: Dict[str, Signal]) -> Signal:
        # Render a sine signal
        result = Signal()
        ts: np.ndarray = self.sample_range_to_times(start, samples)
        result[0] = 0.5 - 0.5 * np.cos(ts * np.pi * 2 * 440)
        return result


class SineSignal(RouterComponent):

    def __init__(self, id: int):
        super().__init__(id)
        self.add_output_node("Out")
        self.content = Gtk.DrawingArea()
        self.content.connect("draw", self.on_draw)
        self.content.set_size_request(64, 32)

    def on_draw(self, widget: Gtk.Widget, context: cairo.Context):
        width = widget.get_allocated_width()
        height = widget.get_allocated_height()
        context.set_source_rgb(0.0, 0.0, 0.0)

        ts = np.linspace(0, 1, 50)
        ss = np.sin(ts * np.pi * 4) * 0.5 + 0.5

        context.move_to(0, height // 2)
        for t, s in zip(ts, ss):
            x = t * width
            y = (s * 0.8 + 0.1) * height
            context.line_to(x, y)
        context.stroke()
