from jackdaw.Data.ProjectData import RouterComponentData
from jackdaw.UI.RouterComponent import RouterComponent
from jackdaw.Gi import Gtk


class PassThroughData(RouterComponentData):

    def create_component(self, id: int):
        return PassThrough(id)


class PassThrough(RouterComponent):

    def __init__(self, id: int):
        super().__init__(id)
        self.add_input_node("In")
        self.add_output_node("Out")
        self.content = Gtk.Label(label="Pass through")
