from jackdaw.Data.ProjectData import RouterComponentData
from jackdaw.UI.RouterComponent import RouterComponent
from jackdaw.Gi import Gtk


class MasterOutputData(RouterComponentData):

    def create_component(self, id: int):
        return MasterOutput(id)


class MasterOutput(RouterComponent):

    def __init__(self, id: int):
        super().__init__(id)
        self.add_input_channel("To Master")
        self.content = Gtk.Label(label="Master output")
