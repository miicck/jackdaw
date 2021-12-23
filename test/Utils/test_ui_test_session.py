from .UiTestSession import UiTestSession
from jackdaw.Data.ProjectData import ProjectData


def test_ui_closed_properly():
    with UiTestSession():
        pass

    assert not ProjectData.instance_exists()
