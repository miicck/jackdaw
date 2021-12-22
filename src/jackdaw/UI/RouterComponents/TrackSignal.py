from jackdaw.UI.RouterComponent import RouterComponent
from jackdaw.Gi import Gtk


class TrackSignal(RouterComponent):

    def __init__(self):
        super().__init__()
        self.content = Gtk.ScrolledWindow()
        self.content.set_size_request(128, 128)

        self.add_input_channel()
        self.add_input_channel("Input channel 1")
        self.add_input_channel("")

        self.add_output_channel("Track")
        self.add_output_channel()
        self.add_output_channel("Long output name")
