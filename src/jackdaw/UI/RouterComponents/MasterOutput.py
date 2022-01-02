from jackdaw.Data.ProjectData import RouterComponentData
from jackdaw.UI.RouterComponent import RouterComponent
from jackdaw.Rendering.ComponentRenderer import ComponentRenderer
from jackdaw.Gi import Gtk


class MasterOutputData(RouterComponentData):

    def create_component(self, id: int):
        return MasterOutput(id)

    def create_component_renderer(self):
        return MasterOutputRenderer()


class MasterOutputRenderer(ComponentRenderer):
    pass


class MasterOutput(RouterComponent):

    def __init__(self, id: int):
        super().__init__(id)
        self.add_input_node("To Master")
        self.content = Gtk.Label(label="Master output")
