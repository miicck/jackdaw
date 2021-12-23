from jackdaw.UI.ControlPanel import ControlPanel
from jackdaw.Gi import Gtk, add_timeout
from jackdaw.TimeControl import TimeControl
from jackdaw.Session import call_session_close_methods


def start_main_loop():
    ControlPanel.instance()
    add_timeout(TimeControl.update, 16, repeats=0)
    Gtk.main()
    call_session_close_methods()


if __name__ == "__main__":  # pragma: no cover
    start_main_loop()
