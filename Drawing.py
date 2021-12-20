from Gi import Gtk
import cairo
from Colors import Colors
from typing import Callable


def draw_background_grid(area: Gtk.DrawingArea, context: cairo.Context,
                         row_height: int, sub_beat_width: int,
                         is_dark_row: Callable[[int], bool]):
    # Get the height/width of the drawing area
    height = area.get_allocated_height()
    width = area.get_allocated_width()

    # Fill background
    context.set_source_rgb(*Colors.background)
    context.rectangle(0, 0, width, height)
    context.fill()

    # Fill dark rows
    context.set_source_rgb(*Colors.background_black_key)
    for i in range(1 + height // row_height):
        if is_dark_row(i):
            context.rectangle(0, i * row_height, width, row_height)
    context.fill()

    # Draw sub-beat markers
    context.set_source_rgb(*Colors.sub_beat_marker)
    for i in range(1 + width // sub_beat_width):
        context.move_to(i * sub_beat_width, 0)
        context.line_to(i * sub_beat_width, height)
    context.stroke()

    # Draw row separators
    context.set_source_rgb(*Colors.track_seperator)
    for i in range(1 + height // row_height):
        context.move_to(0, i * row_height)
        context.line_to(width, i * row_height)
    context.stroke()

    # Draw beat markers
    context.set_source_rgb(*Colors.beat_marker)
    beat_width = sub_beat_width * 4
    for i in range(1 + width // beat_width):
        context.move_to(i * beat_width, 0)
        context.line_to(i * beat_width, height)
    context.stroke()

    # Draw bar markers
    bar_width = beat_width * 4
    context.set_source_rgb(*Colors.bar_marker)
    for i in range(1 + width // bar_width):
        context.move_to(i * bar_width, 0)
        context.line_to(i * bar_width, height)
    context.stroke()
