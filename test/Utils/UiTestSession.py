import time
from jackdaw.Gi import Gtk, add_timeout
from jackdaw.TimeControl import TimeControl
from jackdaw.Main import start_main_loop
from jackdaw.Data.ProjectData import ProjectData
import os


class UiTestSession:

    def __init__(self, main_loop_ms=200, pause_after_ms=100, save_project=False):
        self.main_loop_ms = main_loop_ms
        self.pause_after_ms = pause_after_ms
        self.save_project = save_project

        TimeControl.play()
        add_timeout(Gtk.main_quit, main_loop_ms)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        start_main_loop()
        time.sleep(self.pause_after_ms / 1000.0)

        if not self.save_project:
            if os.path.isfile(ProjectData.FILENAME):
                os.remove(ProjectData.FILENAME)
