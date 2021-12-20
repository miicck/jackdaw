from Gi import Gtk, Gdk
import cairo
from UI.MidiEditor import MidiEditor
from UI.Colors import Colors


class PlaylistClip(Gtk.DrawingArea):

    def __init__(self, clip_number, track: int, beat: float):
        super().__init__()
        self.clip_number = clip_number
        self.track = track
        self.beat = beat
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
            self.open_midi_editor()
            return

    def open_midi_editor(self):
        return MidiEditor.open(self.clip_number)

    def save_to_line(self) -> str:
        return f"{self.clip_number} {self.track} {self.beat}"

    @staticmethod
    def load_from_line(line: str) -> [int, int, float]:
        line = line.split()
        return int(line[0]), int(line[1]), float(line[2])

    def draw_clip(self, area: Gtk.DrawingArea, context: cairo.Context):
        width = area.get_allocated_width()
        height = area.get_allocated_height()

        context.set_source_rgba(*Colors.playlist_clip)
        context.rectangle(1, 1, width - 2, height - 2)
        context.fill()

        font_size = height // 5
        context.set_font_size(font_size)
        context.set_source_rgb(0.0, 0.0, 0.0)
        context.move_to(1, font_size)
        context.show_text(f"{self.clip_number}")
