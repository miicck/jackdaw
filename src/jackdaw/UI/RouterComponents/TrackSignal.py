from jackdaw.UI.RouterComponent import RouterComponent
from jackdaw.Gi import Gtk


class TrackSignal(RouterComponent):

    def __init__(self):
        super().__init__()

        self.add(Gtk.Label(label="Track signal"))
