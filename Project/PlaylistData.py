from Session import session_close_method
from Project import Filestructure as FS


class PlaylistData:

    def __init__(self):
        self.filename = f"{FS.DATA_DIR}/playlist.jdp"

    def load(self):
        pass

    def save(self):
        pass

    ################
    # STATIC STUFF #
    ################

    _loaded_data = None

    @staticmethod
    def get():
        if PlaylistData._loaded_data is None:
            PlaylistData._loaded_data = PlaylistData()

        return PlaylistData._loaded_data

    @staticmethod
    @session_close_method
    def unload():
        PlaylistData._loaded_data = None
