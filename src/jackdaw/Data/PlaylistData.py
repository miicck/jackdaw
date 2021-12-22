from jackdaw.Session import session_close_method
from jackdaw.Data import Filestructure as FS
from jackdaw.Data.LineSerializable import LineSerializableCollection
from jackdaw.Data.PlaylistClipData import PlaylistClipData


class PlaylistData(LineSerializableCollection[PlaylistClipData]):

    def __init__(self):
        super().__init__()
        self.load(PlaylistClipData.load_from_line)

    @property
    def filename(self) -> str:
        return f"{FS.DATA_DIR}/playlist.jdp"

    @property
    def clips(self):
        return self.data

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