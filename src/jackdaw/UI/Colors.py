from typing import Tuple
import random


class Colors:
    background = (0.3, 0.3, 0.3)
    background_black_key = (0.28, 0.28, 0.28)
    track_seperator = (0.25, 0.25, 0.25)
    bar_marker = (0.0, 0.0, 0.0)
    beat_marker = (0.25, 0.25, 0.25)
    sub_beat_marker = (0.27, 0.27, 0.27)
    playlist_clip = (0.5, 0.5, 0.5, 0.5)
    playlist_midi_note = (0.6, 0.6, 0.6)
    router_component_header = (0.2, 0.2, 0.2)
    routing_node_border = (0.5, 0.5, 0.5)
    routing_node_centre = (0.2, 0.2, 0.2)

    _playlist_clip_colors = None

    @staticmethod
    def playlist_clip_colors(clip_number: int) -> Tuple[float, float, float, float]:

        if Colors._playlist_clip_colors is None:
            random.seed(1024)

            def get_next(previous):
                c = [p + random.random() for p in previous]
                c = [p if p < 1 else p - 1 for p in c]
                return c

            cols = [[0.0, 0.0, 1.0]]
            while len(cols) < 100:
                cols.append(get_next(cols[-1]))

            def remap(col):
                return col * 0.5 + 0.25

            Colors._playlist_clip_colors = [(remap(c[0]), remap(c[1]), remap(c[2]), 0.5) for c in cols]

        return Colors._playlist_clip_colors[clip_number % len(Colors._playlist_clip_colors)]
