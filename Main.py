from UI.ControlPanel import ControlPanel
from Gi import Gtk, Gdk, GLib
from TimeControl import TimeControl


def start_main_loop():
    Gdk.threads_add_timeout(GLib.PRIORITY_HIGH_IDLE, 16, lambda e: TimeControl.update(), None)
    Gtk.main()


def open_project_in_current_dir():
    cp = ControlPanel()
    start_main_loop()


if __name__ == "__main__":
    open_project_in_current_dir()
