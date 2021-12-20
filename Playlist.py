import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk

from MidiEditor import MidiEditor


class Playlist(Gtk.Window):

    def __init__(self):
        super().__init__(title="Playlist")
        self.set_default_size(800, 800)

        scroll_area = Gtk.ScrolledWindow()
        self.add(scroll_area)

        rows = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        scroll_area.add(rows)

        for i in range(100):
            row = Gtk.Box()
            rows.add(row)

            drop = Gtk.ComboBoxText()
            drop.append_text("MIDI")
            drop.append_text("AUTO")
            drop.append_text("AUDIO")
            drop.set_active(0)
            row.add(drop)

            label = str(i)
            while len(label) < len("1000"):
                label = "0" + label

            label = Gtk.Label(label=label)
            row.add(label)

            sep = Gtk.Separator()
            rows.add(sep)

            row_button = Gtk.Button(label="edit")
            row_button.connect("clicked", lambda e, i=i: self.open_midi_editor(i))
            row.add(row_button)

        self.show_all()

    def open_midi_editor(self, track):
        MidiEditor(track)
