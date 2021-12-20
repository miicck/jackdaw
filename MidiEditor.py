import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk
import cairo
from MidiNote import MidiNote


class MidiEditor(Gtk.Window):

    def __init__(self, track_number):
        super().__init__(title=f"Midi Editor (track {track_number})")

        self.set_default_size(800, 800)
        self.key_height = 20  # The height in px of a keyboard key

        # Set up the keys to display
        self.keys = []
        for octave in range(8):
            for note in ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]:
                self.keys.append(f"{note}{octave}")

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

        self.show_all()

    def on_click(self, area: Gtk.DrawingArea, button: Gdk.EventButton):

        if button.button == Gdk.BUTTON_PRIMARY:
            self.add_note(area, button)
            return

    def add_note(self, area: Gtk.DrawingArea, button: Gdk.EventButton):
        height = area.get_allocated_height()

        # Work out which note was clicked
        key_index = int(height - button.y) // self.key_height
        if key_index < 0 or key_index >= len(self.keys):
            return  # Invalid key

        # Get snapped x,y position
        y = height - (key_index + 1) * self.key_height
        x = (int(button.x + self.sub_beat_width // 2) // self.sub_beat_width) * self.sub_beat_width

        note = MidiNote()
        note.set_size_request(self.beat_width - 2, self.key_height - 2)
        self.notes_area.put(note, x + 1, y + 1)
        self.notes_area.show_all()

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
        height = area.get_allocated_height()
        width = area.get_allocated_width()

        # Colors
        background = 0.3
        background_black_key = 0.28
        key_sep = 0.25
        bar_mark = 0.0
        beat_mark = 0.25
        sub_beat_mark = 0.27

        # Fill background
        context.set_source_rgb(background, background, background)
        context.rectangle(0, 0, width, height)
        context.fill()

        # Fill black key background
        context.set_source_rgb(*[background_black_key] * 3)
        for i, k in enumerate(self.keys):
            if "#" in k:
                y = height - (i + 1) * self.key_height
                context.rectangle(0, y, width, self.key_height)
        context.fill()

        # Draw sub-beat markers
        context.set_source_rgb(sub_beat_mark, sub_beat_mark, sub_beat_mark)
        for i in range(width // self.sub_beat_width):
            context.move_to(i * self.sub_beat_width, 0)
            context.line_to(i * self.sub_beat_width, height)
        context.stroke()

        # Draw key separators
        context.set_source_rgb(key_sep, key_sep, key_sep)
        for i in range(height // self.key_height):
            context.move_to(0, i * self.key_height)
            context.line_to(width, i * self.key_height)
        context.stroke()

        # Draw beat markers
        context.set_source_rgb(beat_mark, beat_mark, beat_mark)
        for i in range(width // self.beat_width):
            context.move_to(i * self.beat_width, 0)
            context.line_to(i * self.beat_width, height)
        context.stroke()

        # Draw bar markers
        context.set_source_rgb(bar_mark, bar_mark, bar_mark)
        for i in range(width // self.bar_width):
            context.move_to(i * self.bar_width, 0)
            context.line_to(i * self.bar_width, height)
        context.stroke()
