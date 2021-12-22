from jackdaw.UI.ControlPanel import ControlPanel
from jackdaw.Gi import Gtk, add_timeout
from jackdaw.TimeControl import TimeControl


def start_main_loop():
    add_timeout(TimeControl.update, 16, repeats=0)
    Gtk.main()


if __name__ == "__main__":  # pragma: no cover
    ControlPanel()
    start_main_loop()
