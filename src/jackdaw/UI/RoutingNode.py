import cairo
from jackdaw.Gi import Gtk, Gdk
from jackdaw.UI.Colors import Colors
from typing import Callable


class RoutingNode(Gtk.Box):

    def __init__(self, channel_name: str, is_output: bool, label: str = None):
        super().__init__()

        self._channel_name = channel_name
        self._is_output = is_output
        self._mouse_inside = False

        node = Gtk.DrawingArea()
        node.add_events(Gdk.EventMask.ENTER_NOTIFY_MASK |
                        Gdk.EventMask.LEAVE_NOTIFY_MASK |
                        Gdk.EventMask.BUTTON_PRESS_MASK)

        node.connect("draw", self.on_draw)
        node.connect("enter-notify-event", self.on_mouse_enter)
        node.connect("leave-notify-event", self.on_mouse_leave)
        node.set_size_request(32, 32)
        self.node = node

        self.label = Gtk.Label(label=label)
        self.label.set_opacity(0.0)

        packer = self.pack_start if self.is_output else self.pack_end
        packer(node, False, True, 0)
        packer(self.label, False, True, 0)

        self.show_all()

    def add_click_event(self, callback: Callable[[Gdk.EventButton], None]):
        self.node.connect("button-press-event", lambda w, b: callback(b))

    def node_coordinates(self):
        size = min(self.node.get_allocated_width(), self.node.get_allocated_height())
        return self.node.translate_coordinates(self, size // 2, size // 2)

    ##############
    # PROPERTIES #
    ##############

    @property
    def is_output(self):
        return self._is_output

    ###################
    # EVENT CALLBACKS #
    ###################

    def on_mouse_enter(self, widget: Gtk.Widget, event: Gdk.EventCrossing):
        self._mouse_inside = True
        self.label.set_opacity(1.0)
        self.queue_draw()

    def on_mouse_leave(self, widget: Gtk.Widget, event: Gdk.EventCrossing):
        self._mouse_inside = False
        self.label.set_opacity(0.0)
        self.queue_draw()

    def on_draw(self, widget: Gtk.Widget, context: cairo.Context):
        width = widget.get_allocated_width()
        height = widget.get_allocated_height()

        size = min(width, height)
        half = size // 2
        x_centre = half if self.is_output else width - half
        y_centre = half

        size -= 4
        half -= 2

        col = Colors.routing_node_border
        if self._mouse_inside:
            col = [1.0, 0.0, 0.0]

        context.set_source_rgb(*col)
        context.arc(x_centre, y_centre, half, 0, 3.14159 * 2)
        context.fill()

        context.set_source_rgb(*Colors.routing_node_centre)
        context.arc(x_centre, y_centre, half // 2, 0, 3.14159 * 2)
        context.fill()
