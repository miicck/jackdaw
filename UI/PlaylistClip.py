import os.path

from Gi import Gtk, Gdk
import cairo
from UI.MidiEditor import MidiEditor
from UI.MidiNote import MidiNote
from UI.Colors import Colors
from Data import Filestructure as FS
from Data.PlaylistClipData import PlaylistClipData
from typing import Callable
from Data import data


class PlaylistClip(Gtk.DrawingArea):

    def __init__(self, clip: PlaylistClipData):
        super().__init__()

        # Initialize parameters
        self.clip = clip
        self._delete_clip_callbacks = []

        # Connect draw event
        self.connect("draw", self.draw_clip)

        # Connect mouse click event
        self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.connect("button-press-event", self.on_click)

    def on_click(self, area: Gtk.DrawingArea, button: Gdk.EventButton):

        if button.button == Gdk.BUTTON_SECONDARY:
            # Destroy note on right click
            for c in self._delete_clip_callbacks:
                c(self)
            self.destroy()
            return

        if button.button == Gdk.BUTTON_PRIMARY:
            # Open midi editor on double left click
            if button.type == Gdk.EventType.DOUBLE_BUTTON_PRESS:
                MidiEditor.open(self.clip.clip_number)

            from UI.Playlist import Playlist
            Playlist.paste_clip_number = self.clip.clip_number
            return

    def draw_clip(self, area: Gtk.DrawingArea, context: cairo.Context):
        width = area.get_allocated_width()
        height = area.get_allocated_height()

        context.set_source_rgba(*Colors.playlist_clip)
        context.rectangle(1, 1, width - 2, height - 2)
        context.fill()

        self.draw_midi_preview(area, context)

        font_size = height // 5
        context.set_font_size(font_size)
        context.set_source_rgb(0.0, 0.0, 0.0)
        context.move_to(1, font_size)
        context.show_text(f"{self.clip.clip_number}")

    def add_delete_clip_listener(
            self, callback: Callable[['PlaylistClip'], None]):
        self._delete_clip_callbacks.append(callback)

    def draw_midi_preview(self, area: Gtk.DrawingArea, context: cairo.Context):

        # Midi drawing area has a 1px borer
        width = area.get_allocated_width() - 2
        height = area.get_allocated_height() - 2

        # Read the notes from the file
        notes = []
        for note in data.midi_clip(self.clip.clip_number).notes:
            notes.append((MidiEditor.note_name_to_index(note.note), note.beat))

        # No notes to draw
        if len(notes) == 0:
            return

        # Sort notes by index/get effective index range
        notes.sort()
        min_index = notes[0][0] - 1
        max_index = notes[-1][0] + 1

        context.set_source_rgb(*Colors.playlist_midi_note)
        for index, beat in notes:
            # How far up the index range this note is
            frac = (index - min_index) / (max_index - min_index)
            y = int((1 - frac) * height)
            x = int(beat * width / 4)
            context.rectangle(x + 1, y + 1,
                              width // 4 - 1,
                              height // (max_index - min_index))
        context.fill()
