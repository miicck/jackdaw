from jackdaw.UI.RouterComponent import RouterComponent
from jackdaw.Gi import Gtk


class TrackSignal(RouterComponent):

    def __init__(self, id: int):
        super().__init__(id)
        self.content = Gtk.Button(label="Track")

        self.add_input_channel("Input channel 0")
        self.add_input_channel("Input channel 1")
        self.add_input_channel("Input channel 2")

        self.add_output_channel("Track")
        self.add_output_channel("Output name")
        self.add_output_channel("Long output name")
