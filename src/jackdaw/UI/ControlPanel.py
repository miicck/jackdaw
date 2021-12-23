from jackdaw.Gi import Gtk, Gdk, GLib
from jackdaw.UI.Router import Router
from jackdaw.UI.Playlist import Playlist
from jackdaw.TimeControl import TimeControl
from jackdaw.RuntimeChecks import must_be_called_from
from jackdaw.Session import session_close_method


class ControlPanel(Gtk.Window):

    def __init__(self):
        super().__init__(title="Control panel")
        must_be_called_from(ControlPanel.open)

        self.connect("destroy", Gtk.main_quit)

        buttons = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(buttons)

        buttons.add(Gtk.Label(label="\nTime controls\n"))

        play_button = Gtk.Button(label="Play")
        play_button.connect("clicked", lambda e: TimeControl.play())
        buttons.add(play_button)

        pause_button = Gtk.Button(label="Pause")
        pause_button.connect("clicked", lambda e: TimeControl.pause())
        buttons.add(pause_button)

        stop_button = Gtk.Button(label="Stop")
        stop_button.connect("clicked", lambda e: TimeControl.stop())
        buttons.add(stop_button)

        buttons.add(Gtk.Label(label="\nWindows\n"))

        playlist_button = Gtk.Button(label="Show playlist")
        playlist_button.connect("clicked", lambda e: Playlist.open())
        buttons.add(playlist_button)

        playlist_button = Gtk.Button(label="Show router")
        playlist_button.connect("clicked", lambda e: Router.open())
        buttons.add(playlist_button)

        self.show_all()

    ################
    # STATIC STUFF #
    ################

    _open_control_panel = None

    @staticmethod
    def open():
        if ControlPanel._open_control_panel is None:
            ControlPanel._open_control_panel = ControlPanel()
        return ControlPanel._open_control_panel

    @staticmethod
    @session_close_method
    def close():
        if ControlPanel._open_control_panel is not None:
            ControlPanel._open_control_panel.destroy()
        ControlPanel._open_control_panel = None
