from jackdaw.Data.RouterComponentData import RouterComponentData
from jackdaw.Data.LineSerializable import LineSerializableCollection
from jackdaw.Data import Filestructure as FS
from jackdaw.Session import session_close_method
from jackdaw.RuntimeChecks import must_be_called_from
from typing import List


class RouterData(LineSerializableCollection[RouterComponentData]):

    def __init__(self):
        must_be_called_from(RouterData.get)
        super().__init__()
        self.load(RouterComponentData.load_from_line)

    @property
    def filename(self) -> str:
        return f"{FS.DATA_DIR}/router.jdr"

    @property
    def components(self) -> List[RouterComponentData]:
        return self.data

    ################
    # STATIC STUFF #
    ################

    _loaded_data = None

    @staticmethod
    def get():
        if RouterData._loaded_data is None:
            RouterData._loaded_data = RouterData()
        return RouterData._loaded_data

    @staticmethod
    @session_close_method
    def unload():
        RouterData._loaded_data = None
