from UI.ControlPanel import ControlPanel
from Gi import Gtk, Gdk, GLib
from TimeControl import TimeControl


def start_main_loop():
    Gdk.threads_add_timeout(GLib.PRIORITY_HIGH_IDLE, 16, TimeControl.update, None)
    Gtk.main()


if __name__ == "__main__":
    cp = ControlPanel()
    start_main_loop()
