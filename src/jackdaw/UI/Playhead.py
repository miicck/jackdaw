import cairo
from typing import Callable
from jackdaw.Gi import Gtk
from jackdaw.TimeControl import TimeControl


class Playhead(Gtk.DrawingArea):

    def __init__(self):
        super().__init__()
        self.connect("draw", self.draw_playhead)
        self._position_callback = None
        Playhead.playheads.add(self)

    def set_position_callback(self, position_callback: Callable[[float], None]):
        self._position_callback = position_callback

    def draw_playhead(self, area: Gtk.DrawingArea, context: cairo.Context):
        width = area.get_allocated_width()
        height = area.get_allocated_height()

        context.set_source_rgba(1.0, 1.0, 1.0, 0.5)
        context.rectangle(0, 0, 2, height)
        context.fill()

    def invoke_position_callback(self):
        if self._position_callback is not None:
            self._position_callback(TimeControl.get_time())

    playheads = set()
