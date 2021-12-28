from jackdaw.Data.ProjectData import RouterComponentData
from jackdaw.UI.RouterComponent import RouterComponent
from jackdaw.Rendering.ComponentRenderer import ComponentRenderer
from jackdaw.Gi import Gtk
import cairo
import numpy as np
from typing import Dict


class SineSignalData(RouterComponentData):

    def create_component(self, id: int):
        return SineSignal(id)

    def create_component_renderer(self):
        return SineSignalRenderer()


class SineSignalRenderer(ComponentRenderer):

    def render_output_signal(self, node: str, channel: int, start: int, samples: int):
        # Only render the output node on channel 0
        if node != "Out" or channel != 0:
            return None

        # Render a sine signal
        ts: np.ndarray = self.sample_range_to_times(start, samples)
        return np.sin(ts * np.pi * 2 * 440)

    def render(self, output_node: str, channel: int,
               input_node_signals: Dict[str, Dict[int, np.ndarray]]) -> Dict[int, np.ndarray]:
        # Ensure we don't have any input signals
        assert len(input_node_signals) == 0

        # Render a sine signal
        ts: np.ndarray = self.sample_range_to_times(0, 256)
        return {0: np.sin(ts * np.pi * 2 * 440)}


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
