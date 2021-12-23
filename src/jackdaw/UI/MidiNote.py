import cairo
from typing import Callable
from jackdaw.Gi import Gtk, Gdk


class MidiNote(Gtk.DrawingArea):

    def __init__(self):
        super().__init__()
        self._delete_note_callbacks = []

        # Connect draw event
        self.connect("draw", self.on_draw_note)

        # Add button press events
        self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.connect("button-press-event", self.on_click)

    def add_delete_note_listener(self, callback: Callable[[], None]):
        self._delete_note_callbacks.append(callback)

    def delete(self):
        for c in self._delete_note_callbacks:
            c()
        self.destroy()

    ###################
    # EVENT LISTENERS #
    ###################

    def on_click(self, area: Gtk.DrawingArea, button: Gdk.EventButton):
        if button.button == Gdk.BUTTON_SECONDARY:
            # Delete note on right click
            self.delete()
            return

    def on_draw_note(self, area: Gtk.DrawingArea, context: cairo.Context):
        width = area.get_allocated_width()
        height = area.get_allocated_height()
        context.set_source_rgba(1.0, 1.0, 1.0, 0.5)
        context.rectangle(1, 1, width - 2, height - 2)
        context.fill()
