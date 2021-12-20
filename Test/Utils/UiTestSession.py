import time
from Gi import Gtk, Gdk, GLib
from TimeControl import TimeControl


class UiTestSession:

    def __init__(self, main_loop_ms=100, pause_after_ms=100):
        TimeControl.play()
        self.pause_after_ms = pause_after_ms
        Gdk.threads_add_timeout(GLib.PRIORITY_HIGH_IDLE, main_loop_ms, self.stop_session, None)

    def stop_session(self, e):
        # Close all open things
        for m in UiTestSession.close_methods:
            m()

        # Perform a main quit
        Gtk.main_quit()
        return False

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        from Main import start_main_loop
        start_main_loop()
        TimeControl.stop()
        time.sleep(self.pause_after_ms / 1000.0)

    close_methods = set()

    @staticmethod
    def add_close_method(method: callable):
        UiTestSession.close_methods.add(method)
