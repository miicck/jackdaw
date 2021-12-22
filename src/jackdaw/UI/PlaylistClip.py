import cairo
from typing import Callable
from jackdaw.Gi import Gtk, Gdk
from jackdaw.UI.MidiEditor import MidiEditor
from jackdaw.UI.Colors import Colors
from jackdaw.Data.PlaylistClipData import PlaylistClipData
from jackdaw.Data.MidiClipData import MidiClipData
from jackdaw.Data import data
from jackdaw.TimeControl import TimeControl


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

        if button.button == Gdk.BUTTON_PRIMARY:
            # Open midi editor on double left click
            if button.type == Gdk.EventType.DOUBLE_BUTTON_PRESS:
                MidiEditor.open(self.clip.clip_number)

            # Set the playhead to the start of this clip
            TimeControl.set_playhead_time(TimeControl.beats_to_time(self.clip.beat))

            # Set the clip number we're pasting to this clip
            from UI.Playlist import Playlist
            Playlist.paste_clip_number = self.clip.clip_number
            return

        if button.button == Gdk.BUTTON_SECONDARY:
            # Delete note on right click
            self.delete()
            return

        if button.button == Gdk.BUTTON_MIDDLE:
            # Make unique on middle click
            self.make_unique()
            return

    def make_unique(self):

        # Get a unique clip number
        numbers = set(MidiClipData.clips_on_disk())
        if len(numbers) > 0:
            unique_number = max(numbers) + 1
            for i in range(1, unique_number + 1):
                if i not in numbers:
                    unique_number = i
                    break
        else:
            unique_number = 1

        # Copy MIDI data from this clip
        midi = MidiClipData.get(unique_number)
        old_midi = MidiClipData.get(self.clip.clip_number)
        for note in old_midi.notes:
            midi.add(note.copy())

        # Create the new clip
        new_data = PlaylistClipData(unique_number, self.clip.track, self.clip.beat)
        data.playlist.add(new_data)

        # Delete me
        self.delete()

    def delete(self):
        for c in self._delete_clip_callbacks:
            c(self)
        self.destroy()

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

        # Get effective index range
        min_index = min(n[0] for n in notes) - 1
        max_index = max(n[0] for n in notes) + 1

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
