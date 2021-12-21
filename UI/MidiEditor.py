import TimeControl
from Gi import Gtk, Gdk
import cairo
from UI.MidiNote import MidiNote
from UI.Playhead import Playhead
from TimeControl import TimeControl
from UI.Drawing import draw_background_grid
from Session import session_close_method
import MusicTheory
from Data.MidiNoteData import MidiNoteData as MidiNoteData
from Data.MidiClipData import MidiClipData as MidiClipData
from Data import data


class MidiEditor(Gtk.Window):
    # The currently-open Midi editors
    open_editors = dict()
    MAX_OCTAVE = 8

    class NoteOutOfRangeException(Exception):
        def __init__(self, message):
            self.message = message

    # Open a midi editor for a given clip
    @staticmethod
    def open(clip_number: int):
        if clip_number in MidiEditor.open_editors:
            editor = MidiEditor.open_editors[clip_number]
        else:
            editor = MidiEditor(clip_number)
            MidiEditor.open_editors[clip_number] = editor

        assert editor.clip.clip_number == clip_number
        editor.present()
        return editor

    @staticmethod
    @session_close_method
    def close_all():
        for clip_number in list(MidiEditor.open_editors):
            MidiEditor.close(clip_number)

    @staticmethod
    def close(clip_number: int):
        if clip_number in MidiEditor.open_editors:
            MidiEditor.open_editors[clip_number].destroy()
            assert clip_number not in MidiEditor.open_editors

    @staticmethod
    def note_name_to_index(name: str):
        if "#" in name:
            octave = int(name[2:])
            note = name[:2]
        else:
            octave = int(name[1:])
            note = name[0]
        return octave * 12 + MusicTheory.NOTES.index(note)

    def __init__(self, clip_number: int):
        super().__init__(title=f"Midi Editor (clip {clip_number})")

        self.clip = data.midi_clip(clip_number)
        self.clip.add_change_listener(self.on_clip_change)

        self.set_default_size(800, 800)
        self.key_height = 16  # The height in px of a keyboard key

        # Set up the keys to display
        self.keys = []
        self.key_indicies = {}
        for octave in range(MidiEditor.MAX_OCTAVE + 1):
            for note in MusicTheory.NOTES:
                name = f"{note}{octave}"
                self.key_indicies[name] = len(self.keys)
                self.keys.append(name)

        for name in self.key_indicies:
            assert self.key_indicies[name] == MidiEditor.note_name_to_index(name)

        # Setup widget structure
        scroll_area = Gtk.ScrolledWindow()
        self.add(scroll_area)

        # Box to arrange widgets left-ro-right
        left_right_box = Gtk.Box()
        scroll_area.add(left_right_box)

        # The keyboard bit on the left
        keyboard_area = Gtk.DrawingArea()
        keyboard_area.set_size_request(self.keyboard_depth, self.total_height)
        keyboard_area.connect("draw", self.draw_keyboard)
        left_right_box.pack_start(keyboard_area, False, False, 0)

        # The scrollable area containing notes
        notes_scroll_area = Gtk.ScrolledWindow()
        left_right_box.pack_start(notes_scroll_area, True, True, 0)

        self.notes_area = Gtk.Fixed()
        self.notes_area.set_size_request(8192, self.total_height)
        notes_scroll_area.add(self.notes_area)

        # The bit containing the notes
        notes_background = Gtk.DrawingArea()
        notes_background.set_size_request(8192, self.total_height)
        notes_background.connect("draw", self.draw_background)
        self.notes_area.add(notes_background)

        # Add click event
        notes_background.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        notes_background.connect("button-press-event", self.on_click)

        playhead = Playhead()

        def position_playhead(time):
            x = TimeControl.time_to_beats(time) * self.beat_width
            self.notes_area.move(playhead, x, 0)
            self.notes_area.show_all()

        playhead.set_position_callback(position_playhead)
        playhead.set_size_request(4, self.total_height)
        self.notes_area.add(playhead)
        position_playhead(TimeControl.get_time())

        self.show_all()
        self.connect("destroy", lambda e: MidiEditor.open_editors.pop(self.clip.clip_number))

        # Invoke clip change to load clip data
        self.on_clip_change(self.clip)

    def on_click(self, area: Gtk.DrawingArea, button: Gdk.EventButton):

        if button.button == Gdk.BUTTON_PRIMARY:
            self.paste_note(area, button)
            return

    def on_clip_change(self, clip: MidiClipData):

        # Destroy all the old midi notes in the UI
        for c in self.notes_area.get_children():
            if isinstance(c, MidiNote):
                c.destroy()

        # Create all the new midi notes in the UI
        for note in clip.notes:

            if note.note not in self.key_indicies:
                raise MidiEditor.NoteOutOfRangeException(f"Note: {note.note}")

            # Get the y position of the given note
            height = self.notes_area.get_allocated_height()
            index = self.key_indicies[note.note]
            y = height - (index + 1) * self.key_height

            # Create the note UI
            note_ui = MidiNote(note)
            note_ui.set_size_request(self.beat_width, self.key_height)
            self.notes_area.put(note_ui, self.beat_width * note.beat, y)
            note_ui.add_delete_note_listener(lambda n: clip.remove(n.note))

        self.notes_area.show_all()

    def paste_note(self, area: Gtk.DrawingArea, button: Gdk.EventButton):
        height = area.get_allocated_height()

        # Work out which note was clicked
        key_index = int(height - button.y) // self.key_height
        if key_index < 0 or key_index >= len(self.keys):
            return  # Invalid key
        note = self.keys[key_index]

        # Snap to nearest sub-beat
        beat = (int(button.x) // self.sub_beat_width) / 4.0

        self.clip.add(MidiNoteData(note, beat))

    @property
    def keyboard_depth(self):
        return self.key_height * 4

    @property
    def total_height(self):
        return len(self.keys) * self.key_height

    @property
    def sub_beat_width(self):
        return self.key_height  # Make sub beats square

    @property
    def beat_width(self):
        return self.sub_beat_width * 4

    @property
    def bar_width(self):
        return self.beat_width * 4

    def draw_keyboard(self, area: Gtk.DrawingArea, context: cairo.Context):
        height = area.get_allocated_height()
        width = area.get_allocated_width()

        # Fill with white
        context.set_source_rgb(1.0, 1.0, 1.0)
        context.rectangle(0, 0, width, height)
        context.fill()

        # Draw gaps between white keys
        context.set_source_rgb(0.0, 0.0, 0.0)
        for i, k in enumerate(self.keys):
            if "#" not in k:
                y = height - (i + 1) * self.key_height

                # If the next key is black, shift
                # the gap up so that it is in the
                # middle of the black key
                if i + 1 < len(self.keys):
                    if "#" in self.keys[i + 1]:
                        y -= self.key_height // 2

                context.move_to(0, y)
                context.line_to(width, y)
        context.stroke()

        # Draw white key labels
        context.set_font_size(self.key_height)
        context.set_source_rgb(0.6, 0.6, 0.6)
        for i, k in enumerate(self.keys):
            if "#" not in k:
                y = height - i * self.key_height - 2
                context.move_to(0, y)
                context.show_text(k)

        # Fill in black keys
        context.set_source_rgb(0.0, 0.0, 0.0)
        for i, k in enumerate(self.keys):
            if "#" in k:
                y = height - (i + 1) * self.key_height
                context.rectangle(0, y, width * 3 // 4, self.key_height)

        context.fill()

    def draw_background(self, area: Gtk.DrawingArea, context: cairo.Context):

        def is_dark_row(i):
            if i < 0 or i >= len(self.keys):
                return True
            return "#" in self.keys[-i - 1]

        draw_background_grid(area, context, self.key_height,
                             self.sub_beat_width, is_dark_row)
