from jackdaw.Data.ProjectData import ProjectData


class ProjectDataInstance:

    def __getattribute__(self, item):
        return getattr(ProjectData.instance(), item)

    def __setattr__(self, key, value):
        return setattr(ProjectData.instance(), key, value)


data = ProjectDataInstance()
