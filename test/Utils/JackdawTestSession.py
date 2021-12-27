from jackdaw.Gi import add_timeout
from jackdaw.TimeControl import TimeControl
from jackdaw.Main import start_main_loop
from jackdaw.Data.ProjectData import ProjectData
from jackdaw.UI.ControlPanel import ControlPanel
from jackdaw.Data import data
import os


class JackdawTestSession:

    def __init__(self, main_loop_ms=200, save_project=False, assert_empty_project=True):

        # Set the working directory to jackdaw/test
        test_dir = os.path.dirname(__file__)
        test_dir = test_dir[:test_dir.index("jackdaw/test")] + "jackdaw/test/"
        os.chdir(test_dir)

        self.main_loop_ms = main_loop_ms
        self.save_project = save_project
        self.assert_empty_project = assert_empty_project

    def __enter__(self):
        # Ensure project is empty
        if self.assert_empty_project:
            data.empty_project_assertions()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):

        # Actually start the loop on exit, once all test
        # things are setup inside the context.
        TimeControl.play()
        add_timeout(lambda: ControlPanel.instance().destroy(), self.main_loop_ms)
        start_main_loop()

        if not self.save_project:
            if os.path.isfile(ProjectData.FILENAME):
                os.remove(ProjectData.FILENAME)
