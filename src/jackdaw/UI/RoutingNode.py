import cairo
from jackdaw.Gi import Gtk
from jackdaw.UI.Colors import Colors


class RoutingNode(Gtk.Box):

    def __init__(self, is_output: bool, label: str = None):
        super().__init__()
        self._is_output = is_output

        node = Gtk.DrawingArea()
        node.connect("draw", self.on_draw)
        node.set_size_request(32, 32)

        label = Gtk.Label(label=label)

        packer = self.pack_start if self.is_output else self.pack_end
        packer(node, False, True, 0)
        packer(label, False, True, 0)

        self.show_all()

    def on_draw(self, widget: Gtk.Widget, context: cairo.Context):
        width = widget.get_allocated_width()
        height = widget.get_allocated_height()

        size = min(width, height)
        half = size // 2
        x_centre = half if self.is_output else width - half
        y_centre = half

        size -= 4
        half -= 2

        context.set_source_rgb(*Colors.routing_node_border)
        context.arc(x_centre, y_centre, half, 0, 3.14159 * 2)
        context.fill()

        context.set_source_rgb(*Colors.routing_node_centre)
        context.arc(x_centre, y_centre, half // 2, 0, 3.14159 * 2)
        context.fill()

    @property
    def is_output(self):
        return self._is_output
