import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk

from Playlist import Playlist


class ControlPanel(Gtk.Window):

    def __init__(self):
        super().__init__(title="Control panel")
        self.connect("destroy", Gtk.main_quit)

        buttons = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(buttons)

        playlist_button = Gtk.Button(label="Show playlist")
        playlist_button.connect("clicked", self.show_playlist)
        buttons.add(playlist_button)

        self.show_all()

    def main_loop(self):
        Gtk.main()

    def show_playlist(self, e):
        return Playlist()
