import cairo
from typing import Callable
from jackdaw.Gi import Gtk
from jackdaw.TimeControl import TimeControl
from jackdaw.Session import session_close_method


class Playhead(Gtk.DrawingArea):

    def __init__(self, position_callback: Callable[['Playhead', float], None]):
        super().__init__()
        self.connect("draw", self.on_draw_playhead)
        self._position_callback = position_callback
        Playhead.playheads.add(self)

    def invoke_position_callback(self):
        if self._position_callback is not None:
            self._position_callback(self, TimeControl.get_time())

    def on_draw_playhead(self, area: Gtk.DrawingArea, context: cairo.Context):
        width = area.get_allocated_width()
        height = area.get_allocated_height()

        context.set_source_rgba(1.0, 1.0, 1.0, 0.5)
        context.rectangle(0, 0, 2, height)
        context.fill()

    ################
    # STATIC STUFF #
    ################

    playheads = set()

    @staticmethod
    @session_close_method
    def forget_playheads():
        Playhead.playheads = set()
