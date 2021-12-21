from Project.MidiClip import MidiClip
from Project.PlaylistData import PlaylistData


class ProjectData:

    def __init__(self):
        pass

    def midi_clip(self, clip_number: int) -> MidiClip:
        return MidiClip.get(clip_number)

    @property
    def playlist(self):
        return PlaylistData.get()

    ################
    # STATIC STUFF #
    ################

    _loaded_project = None

    @staticmethod
    def current() -> 'ProjectData':
        """
        :return: The currently loaded project data.
        :rtype: ProjectData
        """
        # Load project if not already loaded
        if ProjectData._loaded_project is None:
            ProjectData._loaded_project = ProjectData()

        # Return loaded project
        return ProjectData._loaded_project
