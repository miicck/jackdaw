import os.path

from Gi import Gtk, Gdk
import cairo
from UI.MidiEditor import MidiEditor
from UI.MidiNote import MidiNote
from UI.Colors import Colors
from Project import Filestructure as FS


class PlaylistClip(Gtk.DrawingArea):

    def __init__(self, clip_number, track: int, beat: float, destroy_callback: callable = None):
        super().__init__()
        self.destroy_callback = destroy_callback
        self.clip_number = clip_number
        self.track = track
        self.beat = beat
        self.connect("draw", self.draw_clip)
        self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.connect("button-press-event", self.on_click)
        self.connect("destroy", self.on_destroy)

    def on_click(self, area: Gtk.DrawingArea, button: Gdk.EventButton):

        if button.button == Gdk.BUTTON_SECONDARY:
            # Destroy note on right click
            self.destroy()
            return

        if button.button == Gdk.BUTTON_MIDDLE:
            # Make clip unique on middle click
            self.make_unique()
            return

        if button.button == Gdk.BUTTON_PRIMARY:
            # Open midi editor on double left click
            if button.type == Gdk.EventType.DOUBLE_BUTTON_PRESS:
                self.open_midi_editor()

            from UI.Playlist import Playlist
            Playlist.paste_clip_number = self.clip_number
            return

    def make_unique(self):
        from UI.Playlist import Playlist
        was_closed = Playlist.open_playlist is None

        # Make unique by picking a new clip number
        pl = Playlist.open()
        old_clip_file = f"{FS.DATA_DIR}/midi/{self.clip_number}.jdm"
        self.clip_number = max(c.clip_number for c in pl.clips) + 1

        # Copy previous clip file if exists
        if os.path.isfile(old_clip_file):
            new_clip_file = f"{FS.DATA_DIR}/midi/{self.clip_number}.jdm"
            os.system(f"cp {old_clip_file} {new_clip_file}")

        # Save new clip number by saving playlist
        pl.save_to_file()

        if was_closed:
            Playlist.close()

    def on_destroy(self, e):
        if self.destroy_callback is not None:
            self.destroy_callback()

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

    def draw_midi_preview(self, area: Gtk.DrawingArea, context: cairo.Context):

        raise NotImplementedError()

        filename = f"{FS.DATA_DIR}/midi/{self.clip_number}.jdm"
        if not os.path.isfile(filename):
            return

        # Midi drawing area has a 1px borer
        width = area.get_allocated_width() - 2
        height = area.get_allocated_height() - 2

        # Read the notes from the file
        notes = []
        with open(filename, "r") as f:
            for line in f:
                name, beat = MidiNote.load_from_line(line)
                index = MidiEditor.note_name_to_index(name)
                notes.append((index, beat))

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
