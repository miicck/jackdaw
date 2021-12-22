import time
from jackdaw.Gi import Gtk, add_timeout
from jackdaw.TimeControl import TimeControl
from jackdaw.Data import Filestructure as FS
from jackdaw.Session import call_session_close_methods
from jackdaw.Main import start_main_loop


class UiTestSession:

    def __init__(self, main_loop_ms=50, pause_after_ms=20, save_project=False):
        self.main_loop_ms = main_loop_ms
        self.pause_after_ms = pause_after_ms
        self.save_project = save_project
        TimeControl.play()

        def stop_session():
            call_session_close_methods()
            Gtk.main_quit()

        add_timeout(stop_session, main_loop_ms)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        start_main_loop()
        TimeControl.stop()
        time.sleep(self.pause_after_ms / 1000.0)

        if not self.save_project:
            FS.delete_project_in_current_dir()
