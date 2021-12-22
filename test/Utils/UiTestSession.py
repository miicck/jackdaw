import time
from jackdaw.Gi import Gtk, Gdk, GLib
from jackdaw.TimeControl import TimeControl
from jackdaw.Data import Filestructure as FS
from jackdaw.Session import call_session_close_methods
from jackdaw.Main import start_main_loop


class UiTestSession:

    def __init__(self, main_loop_ms=100, pause_after_ms=100, save_project=False):
        self.pause_after_ms = pause_after_ms
        self.save_project = save_project
        TimeControl.play()

        def stop_session():
            call_session_close_methods()
            Gtk.main_quit()
            return False  # Don't invoke callback again

        Gdk.threads_add_timeout(GLib.PRIORITY_HIGH_IDLE, main_loop_ms, lambda e: stop_session(), None)

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        start_main_loop()
        TimeControl.stop()
        time.sleep(self.pause_after_ms / 1000.0)

        if not self.save_project:
            FS.delete_project_in_current_dir()
