import cairo
from jackdaw.Gi import Gtk, Gdk
from jackdaw.UI.PlaylistClip import PlaylistClip
from jackdaw.UI.Playhead import Playhead
from jackdaw.UI.Drawing import draw_background_grid
from jackdaw.TimeControl import TimeControl
from jackdaw.Data import data
from jackdaw.Data.ProjectData import PlaylistClipData
from jackdaw.Utils.Singleton import Singleton


class Playlist(Gtk.Window, Singleton):

    def __init__(self):
        Singleton.__init__(self)
        Gtk.Window.__init__(self, title="Playlist")

        self.set_default_size(800, 800)
        data.playlist_clips.add_on_change_listener(self.on_data_change)

        self.track_height = 64
        self.sub_beat_width = 8
        self.total_bars = 128
        self.total_tracks = 100
        self.clips_area = Gtk.Fixed()

        self.setup_clips_area()
        self.setup_background()
        self.setup_playhead()

        self.connect("destroy", lambda e: Playlist.clear_instance())
        self.connect("key-press-event", self.on_keypress)

        # Load initial data + show
        self.on_data_change()
        self.show_all()

    def setup_clips_area(self):
        scroll_area = Gtk.ScrolledWindow()
        self.add(scroll_area)
        self.clips_area.set_size_request(self.clip_area_width, self.clip_area_width)
        scroll_area.add(self.clips_area)

    def setup_background(self):
        background = Gtk.DrawingArea()
        background.set_size_request(self.clip_area_width, self.clip_area_width)
        background.connect("draw", self.on_draw_background)
        background.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        background.connect("button-press-event", self.on_background_click)
        self.clips_area.add(background)

    def setup_playhead(self):
        playhead = Playhead(position_callback=self.position_playhead)
        playhead.set_size_request(4, self.clip_area_height)
        self.clips_area.add(playhead)
        self.position_playhead(playhead, TimeControl.get_time())

    def position_playhead(self, playhead, time):
        x = TimeControl.time_to_beats(time) * self.beat_width
        self.clips_area.move(playhead, x, 0)
        self.clips_area.show_all()

    def paste_clip(self, button: Gdk.EventButton):
        # Get beat/track position
        track = int(button.y) // self.track_height
        beat = int(button.x) // self.beat_width

        new_clip = PlaylistClipData()
        new_clip.clip.value = Playlist.paste_clip_number
        new_clip.track.value = track
        new_clip.beat.value = beat

        data.playlist_clips.add(new_clip)

    ###################
    # EVENT CALLBACKS #
    ###################

    def on_clear_singleton_instance(self):
        self.destroy()

    def on_background_click(self, widget: Gtk.Widget, button: Gdk.EventButton):
        if button.button == Gdk.BUTTON_PRIMARY:
            self.paste_clip(button)

    def on_keypress(self, widget: Gtk.Widget, key: Gdk.EventKey):
        if key.keyval == Gdk.KEY_space:
            TimeControl.toggle_play_stop()

    def on_draw_background(self, area: Gtk.DrawingArea, context: cairo.Context):
        draw_background_grid(area, context, self.track_height, self.sub_beat_width,
                             is_dark_row=lambda i: i % 2 == 0)

    def on_data_change(self):

        # Destroy old clips
        for c in self.ui_clips:
            c.destroy()

        # Create new clips
        for clip in data.playlist_clips:
            x = clip.beat.value * self.beat_width
            y = clip.track.value * self.track_height

            clip_ui = PlaylistClip(clip)
            clip_ui.set_size_request(self.bar_width, self.track_height)
            self.clips_area.put(clip_ui, x, y)
            self.clips_area.show_all()

            clip_ui.add_delete_clip_listener(lambda clip=clip: data.playlist_clips.remove(clip))

    ##############
    # PROPERTIES #
    ##############

    @property
    def ui_clips(self):
        for c in self.clips_area.get_children():
            if isinstance(c, PlaylistClip):
                yield c

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

    ################
    # STATIC STUFF #
    ################

    paste_clip_number = 1
