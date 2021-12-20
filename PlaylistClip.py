from Gi import Gtk, Gdk
import cairo
from MidiEditor import MidiEditor
from Colors import Colors


class PlaylistClip(Gtk.DrawingArea):

    def __init__(self, number):
        super().__init__()
        self.number = number
        self.connect("draw", self.draw_clip)
        self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.connect("button-press-event", self.on_click)

    def on_click(self, area: Gtk.DrawingArea, button: Gdk.EventButton):

        if button.button == Gdk.BUTTON_SECONDARY:
            # Destroy note on right click
            self.destroy()
            return

        if button.button == Gdk.BUTTON_PRIMARY:
            # Open midi editor on left click
            MidiEditor(self.number)
            return

    def draw_clip(self, area: Gtk.DrawingArea, context: cairo.Context):
        width = area.get_allocated_width()
        height = area.get_allocated_height()

        context.set_source_rgba(*Colors.playlist_clip)
        context.rectangle(0, 0, width, height)
        context.fill()

        font_size = height // 5
        context.set_font_size(font_size)
        context.set_source_rgb(0.0, 0.0, 0.0)
        context.move_to(1, font_size)
        context.show_text(f"{self.number}")
