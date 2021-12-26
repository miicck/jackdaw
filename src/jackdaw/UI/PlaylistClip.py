import cairo
from typing import Callable
from jackdaw.Gi import Gtk, Gdk
from jackdaw.UI.MidiEditor import MidiEditor
from jackdaw.UI.Colors import Colors
from jackdaw.Data.ProjectData import PlaylistClipData
from jackdaw.Data import data
from jackdaw.Data.ProjectData import MidiClipData
from jackdaw.TimeControl import TimeControl
import jackdaw.UI.Playlist as PlaylistModule  # Imported this way to avoid circular imports


class PlaylistClip(Gtk.DrawingArea):

    def __init__(self, clip: PlaylistClipData):
        super().__init__()

        # Initialize parameters
        self.clip = clip
        self._delete_clip_callbacks = []

        # Connect draw event
        self.connect("draw", self.on_draw_clip)

        # Connect mouse click event
        self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.connect("button-press-event", self.on_click)

    def delete(self):
        for c in self._delete_clip_callbacks:
            c()
        self.destroy()

    def add_delete_clip_listener(self, callback: Callable[[], None]):
        self._delete_clip_callbacks.append(callback)

    def make_unique(self):

        # Create new midi clip
        new_midi = MidiClipData()

        # Copy old midi clip data (if it exists)
        if self.clip_number in data.midi_clips:
            for note in data.midi_clips[self.clip_number].notes:
                new_midi.notes.add(note.copy())

        # Save new midi clip
        new_key = data.midi_clips.get_unique_key()
        data.midi_clips[new_key] = new_midi

        # Create new playlist clip
        new_clip = self.clip.copy()
        new_clip.clip.value = new_key
        data.playlist_clips.add(new_clip)
        PlaylistModule.Playlist.paste_clip_number = new_key

        # Delete me
        self.delete()

    ##############
    # PROPERTIES #
    ##############

    @property
    def clip_number(self):
        return self.clip.clip.value

    ###################
    # EVENT CALLBACKS #
    ###################

    def on_click(self, area: Gtk.DrawingArea, button: Gdk.EventButton):

        if button.button == Gdk.BUTTON_PRIMARY:
            # Open midi editor on double left click
            if button.type == Gdk.EventType.DOUBLE_BUTTON_PRESS:
                MidiEditor.open(self.clip_number)

            # Set the playhead to the start of this clip
            TimeControl.set_playhead_time(TimeControl.beats_to_time(self.clip.beat.value))

            # Set the clip number we're pasting to this clip
            PlaylistModule.Playlist.paste_clip_number = self.clip_number
            return

        if button.button == Gdk.BUTTON_SECONDARY:
            # Delete note on right click
            self.delete()
            return

        if button.button == Gdk.BUTTON_MIDDLE:
            # Make unique on middle click
            self.make_unique()
            return

    def on_draw_clip(self, area: Gtk.DrawingArea, context: cairo.Context):
        width = area.get_allocated_width()
        height = area.get_allocated_height()

        context.set_source_rgba(*Colors.playlist_clip_colors(self.clip_number))
        context.rectangle(1, 1, width - 2, height - 2)
        context.fill()

        self.draw_midi_preview(area, context)

        font_size = height // 5
        context.set_font_size(font_size)
        context.set_source_rgb(0.0, 0.0, 0.0)
        context.move_to(1, font_size)
        context.show_text(f"{self.clip_number}")

    def draw_midi_preview(self, area: Gtk.DrawingArea, context: cairo.Context):

        # Get the midi clip data to draw (if it exists, otherwise do nothing)
        if self.clip_number not in data.midi_clips:
            return
        midi_clip = data.midi_clips[self.clip_number]

        # Midi drawing area has a 1px borer
        width = area.get_allocated_width() - 2
        height = area.get_allocated_height() - 2

        # Read the notes from the file
        notes = []
        for note in midi_clip.notes:
            notes.append((MidiEditor.note_name_to_index(note.note.value), note.beat.value))

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
