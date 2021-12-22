from jackdaw.Gi import Gtk, Gdk, GLib
from jackdaw.UI.Playlist import Playlist
from jackdaw.TimeControl import TimeControl


class ControlPanel(Gtk.Window):

    def __init__(self):
        super().__init__(title="Control panel")
        self.connect("destroy", Gtk.main_quit)

        buttons = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(buttons)

        playlist_button = Gtk.Button(label="Show playlist")
        playlist_button.connect("clicked", lambda e: Playlist.open())
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
