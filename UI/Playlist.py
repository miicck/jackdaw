from Gi import Gtk, Gdk
import cairo
from UI.Drawing import draw_background_grid
from UI.PlaylistClip import PlaylistClip
from UI.Playhead import Playhead
from TimeControl import TimeControl
from Session import session_close_method
from Project.PlaylistData import PlaylistData
from Project.PlaylistClipData import PlaylistClipData
from Project import data


class Playlist(Gtk.Window):
    open_playlist = None
    paste_clip_number = 1

    @staticmethod
    def open():
        if Playlist.open_playlist is None:
            Playlist.open_playlist = Playlist()

        playlist = Playlist.open_playlist
        playlist.present()
        return playlist

    @staticmethod
    @session_close_method
    def close():
        if Playlist.open_playlist is None:
            return

        Playlist.open_playlist.destroy()

    def __init__(self):
        super().__init__(title="Playlist")
        self.set_default_size(800, 800)
        self.data = data.playlist
        self.data.add_change_listener(self.on_playlist_data_change)

        self.track_height = 64
        self.sub_beat_width = 8
        self.total_bars = 128
        self.total_tracks = 100

        scroll_area = Gtk.ScrolledWindow()
        self.add(scroll_area)

        self.clips_area = Gtk.Fixed()
        self.clips_area.set_size_request(self.clip_area_width, self.clip_area_width)
        scroll_area.add(self.clips_area)

        background = Gtk.DrawingArea()
        background.set_size_request(self.clip_area_width, self.clip_area_width)
        background.connect("draw", self.draw_background)
        self.clips_area.add(background)

        # Add click event
        background.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        background.connect("button-press-event", self.on_click)

        playhead = Playhead()

        def position_playhead(time):
            x = TimeControl.time_to_beats(time) * self.beat_width
            self.clips_area.move(playhead, x, 0)
            self.clips_area.show_all()

        playhead.set_position_callback(position_playhead)
        playhead.set_size_request(4, self.clip_area_height)
        self.clips_area.add(playhead)
        position_playhead(TimeControl.get_time())

        self.show_all()
        self.connect("destroy", self.on_destroy)

        # Load initial playlist data
        self.on_playlist_data_change(self.data)

    def on_destroy(self, e):
        Playlist.open_playlist = None

    def on_click(self, area: Gtk.DrawingArea, button: Gdk.EventButton):
        if button.button == Gdk.BUTTON_PRIMARY:
            self.paste_clip(area, button)

    def paste_clip(self, area: Gtk.DrawingArea, button: Gdk.EventButton):
        # Get beat/track position
        track = int(button.y) // self.track_height
        beat = int(button.x) // self.beat_width
        self.data.add(PlaylistClipData(Playlist.paste_clip_number, track, beat))

    def on_playlist_data_change(self, playlist_data: PlaylistData):

        # Destroy old clips
        for c in self.clips_area.get_children():
            if isinstance(c, PlaylistClip):
                self.clips_area.remove(c)
                c.destroy()

        # Create new clips
        for clip_data in playlist_data.clips:
            clip = PlaylistClip(clip_data)
            clip.set_size_request(self.bar_width, self.track_height)
            self.clips_area.put(clip, clip_data.beat * self.beat_width,
                                clip_data.track * self.track_height)
            self.clips_area.show_all()
            clip.add_delete_clip_listener(lambda c: playlist_data.remove(c.clip))

    @property
    def beat_width(self):
        return self.sub_beat_width * 4

    @property
    def bar_width(self):
        return self.beat_width * 4

    @property
    def clip_area_width(self):
        return self.total_bars * self.bar_width

    @property
    def clip_area_height(self):
        return self.total_tracks * self.track_height

    def draw_background(self, area: Gtk.DrawingArea, context: cairo.Context):
        draw_background_grid(area, context, self.track_height, self.sub_beat_width,
                             is_dark_row=lambda i: i % 2 == 0)
