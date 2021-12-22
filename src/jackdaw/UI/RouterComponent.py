import cairo
from jackdaw.Gi import Gtk, Gdk
from jackdaw.UI.RoutingNode import RoutingNode


class RouterComponent(Gtk.Grid):

    def __init__(self):
        super().__init__()

        self.header_bar = Gtk.DrawingArea()
        self.header_bar.set_size_request(0, 16)
        self.header_bar.add_events(Gdk.EventMask.BUTTON_PRESS_MASK | Gdk.EventMask.BUTTON1_MOTION_MASK)
        self.header_bar.connect("draw", self.on_draw_header)
        self.header_bar.connect("button-press-event", self.on_click_header)
        self.header_bar.connect("motion-notify-event", self.on_drag_header)
        self.drag_start = [0, 0]
        self.attach(self.header_bar, 1, -1, 1, 1)

        self.inputs = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.attach(self.inputs, 0, 0, 1, 1)

        self.outputs = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.attach(self.outputs, 2, 0, 1, 1)

    ############
    # CHANNELS #
    ############

    def add_input_channel(self, label=None):
        input_node = RoutingNode(False, label=label)
        self.inputs.add(input_node)
        self.show_all()

    def remove_input_channel(self):
        raise NotImplementedError()

    def add_output_channel(self, label=None):
        output_node = RoutingNode(True, label=label)
        self.outputs.add(output_node)
        self.show_all()

    def remove_output_channel(self):
        raise NotImplementedError()

    ###################
    # EVENT CALLBACKS #
    ###################

    def on_click_header(self, widget: Gtk.Widget, button: Gdk.EventButton):

        if button.button == Gdk.BUTTON_PRIMARY:
            self.drag_start = [button.x, button.y]
            return

        if button.button == Gdk.BUTTON_SECONDARY:
            self.destroy()
            return

    def on_drag_header(self, widget: Gtk.Widget, button: Gdk.EventButton):
        parent: Gtk.Fixed = self.get_parent()
        if not isinstance(parent, Gtk.Fixed):
            raise Exception("RouterComponent not attached to fixed parent!")

        x, y = self.translate_coordinates(parent, button.x - self.drag_start[0], button.y - self.drag_start[1])
        parent.move(self, x, y)

    def on_draw_header(self, widget: Gtk.Widget, context: cairo.Context):
        width = widget.get_allocated_width()
        height = widget.get_allocated_height()
        context.set_source_rgb(1.0, 1.0, 1.0)
        context.rectangle(0, 0, width, height)
        context.fill()

    ##############
    # PROPERTIES #
    ##############

    @property
    def content(self):
        return self.get_child_at(1, 0)

    @content.setter
    def content(self, value):
        self.attach(value, 1, 0, 1, 1)
