from Gi import Gtk, Gdk, GLib
from Playlist import Playlist
from TimeControl import TimeControl


class ControlPanel(Gtk.Window):

    def __init__(self):
        super().__init__(title="Control panel")
        self.connect("destroy", Gtk.main_quit)

        buttons = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(buttons)

        playlist_button = Gtk.Button(label="Show playlist")
        playlist_button.connect("clicked", self.show_playlist)
        buttons.add(playlist_button)

        play_button = Gtk.Button(label="Play")
        play_button.connect("clicked", lambda e: TimeControl.play())
        buttons.add(play_button)

        pause_button = Gtk.Button(label="Pause")
        pause_button.connect("clicked", lambda e: TimeControl.pause())
        buttons.add(pause_button)

        stop_button = Gtk.Button(label="Stop")
        stop_button.connect("clicked", lambda e: TimeControl.stop())
        buttons.add(stop_button)

        self.show_all()

    def main_loop(self):
        Gdk.threads_add_timeout(GLib.PRIORITY_HIGH_IDLE, 16, TimeControl.update, None)
        Gtk.main()

    def show_playlist(self, e):
        return Playlist()
