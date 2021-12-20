from Gi import Gtk, Gdk
import cairo
from Drawing import draw_background_grid
from PlaylistClip import PlaylistClip


class Playlist(Gtk.Window):

    def __init__(self):
        super().__init__(title="Playlist")
        self.set_default_size(800, 800)

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

        self.show_all()

    def on_click(self, area: Gtk.DrawingArea, button: Gdk.EventButton):
        if button.button == Gdk.BUTTON_PRIMARY:
            self.paste_clip(area, button)

    def paste_clip(self, area: Gtk.DrawingArea, button: Gdk.EventButton):
        # Get snapped x,y position
        x = (int(button.x) // self.sub_beat_width) * self.sub_beat_width
        y = (int(button.y) // self.track_height) * self.track_height

        clip = PlaylistClip(1)
        clip.set_size_request(self.bar_width, self.track_height)
        self.clips_area.put(clip, x, y)
        self.clips_area.show_all()

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
