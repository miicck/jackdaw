from jackdaw.UI.RouterComponent import RouterComponent
from jackdaw.Gi import Gtk
from jackdaw.Data import data
from jackdaw.Data.DataObjects import *
from jackdaw.Data.ProjectData import RouterComponentData


class TrackSignalData(RouterComponentData):

    def __init__(self):
        super().__init__()
        self.track = RawDataObject(0)

    def create_component(self, id: int):
        return TrackSignal(id)


class TrackSignal(RouterComponent):

    def __init__(self, id: int):
        super().__init__(id)
        data.playlist_clips.add_on_change_listener(self.on_playlist_clips_change)
        self.add_output_channel("Track")
        self.on_playlist_clips_change()

    def on_playlist_clips_change(self):

        self.content = Gtk.ComboBoxText()

        tracks = {clip.track.value for clip in data.playlist_clips}.union({0})
        tracks = sorted(list(tracks))

        for i, track in enumerate(tracks):
            self.content.append_text(f"Track {track}")
            if track == self.data.track.value:
                self.content.set_active(i)

        def change_track(index: int):
            self.data.track.value = tracks[index]

        self.content.connect("changed", lambda v: change_track(v.get_active()))
        self.show_all()
