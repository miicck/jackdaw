from Gi import Gtk, Gdk
import cairo


class MidiNote(Gtk.DrawingArea):

    def __init__(self, note: str, beat: float, destroy_callback: callable = None):
        super().__init__()
        self.note = note
        self.beat = beat
        self.destroy_callback = destroy_callback
        self.connect("draw", self.draw_note)
        self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.connect("button-press-event", self.on_click)

    def on_click(self, area: Gtk.DrawingArea, button: Gdk.EventButton):
        if button.button == Gdk.BUTTON_SECONDARY:
            # Destroy note on right click
            if self.destroy_callback is not None:
                self.destroy_callback(self)
            self.destroy()
            return

    def save_to_line(self) -> str:
        return f"{self.note} {self.beat}"

    @staticmethod
    def load_from_line(line: str) -> [str, float]:
        line = line.split()
        return line[0].upper(), float(line[1])

    def draw_note(self, area: Gtk.DrawingArea, context: cairo.Context):
        width = area.get_allocated_width()
        height = area.get_allocated_height()

        context.set_source_rgba(1.0, 1.0, 1.0, 0.5)
        context.rectangle(0, 0, width, height)
        context.fill()
