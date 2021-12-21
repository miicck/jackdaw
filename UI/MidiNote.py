from Gi import Gtk, Gdk
import cairo
from Project.MidiNote import MidiNote as MidiNoteData
from typing import Callable


class MidiNote(Gtk.DrawingArea):

    def __init__(self, note: MidiNoteData):
        super().__init__()
        self.note = note
        self._delete_note_callbacks = []

        # Connect draw event
        self.connect("draw", self.draw_note)

        # Add button press events
        self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.connect("button-press-event", self.on_click)

    def on_click(self, area: Gtk.DrawingArea, button: Gdk.EventButton):
        if button.button == Gdk.BUTTON_SECONDARY:
            # Delete note on right click
            for c in self._delete_note_callbacks:
                c(self)
            self.destroy()
            return

    def draw_note(self, area: Gtk.DrawingArea, context: cairo.Context):
        width = area.get_allocated_width()
        height = area.get_allocated_height()
        context.set_source_rgba(1.0, 1.0, 1.0, 0.5)
        context.rectangle(1, 1, width - 2, height - 2)
        context.fill()

    def add_delete_note_listener(
            self, callback: Callable[['MidiNote'], None]):
        self._delete_note_callbacks.append(callback)
