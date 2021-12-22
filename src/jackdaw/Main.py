from jackdaw.UI.ControlPanel import ControlPanel
from jackdaw.Gi import Gtk, add_timeout
from jackdaw.TimeControl import TimeControl


def start_main_loop():
    add_timeout(TimeControl.update, 16, repeats=0)
    Gtk.main()


def open_project_in_current_dir():
    ControlPanel()
    start_main_loop()


if __name__ == "__main__":
    open_project_in_current_dir()
