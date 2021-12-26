from jackdaw.Data.ProjectData import ProjectData


class ProjectDataInstance:
    """
    A class that forwards attribute access to the ProjectData.instance().
    This is done so that the imported "data" object remains valid, even
    if the instance is cleared/reopened (this happens in the test suite a fair bit).
    """

    def __getattribute__(self, item):
        return getattr(ProjectData.instance(), item)

    def __setattr__(self, key, value):
        return setattr(ProjectData.instance(), key, value)


data: ProjectData = ProjectDataInstance()
