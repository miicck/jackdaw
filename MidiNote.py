import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk
import cairo


class MidiNote(Gtk.DrawingArea):

    def __init__(self):
        super().__init__()
        self.connect("draw", self.draw_note)
        self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.connect("button-press-event", self.on_click)

    def on_click(self, area: Gtk.DrawingArea, button: Gdk.EventButton):
        if button.button == Gdk.BUTTON_SECONDARY:
            # Destroy note on right click
            self.destroy()
            return

    def draw_note(self, area: Gtk.DrawingArea, context: cairo.Context):
        width = area.get_allocated_width()
        height = area.get_allocated_height()

        # context.set_source_rgb(1.0, 1.0, 1.0)
        context.set_source_rgba(1.0, 1.0, 1.0, 0.5)
        context.rectangle(0, 0, width, height)
        context.fill()
