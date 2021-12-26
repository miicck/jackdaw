import cairo
from jackdaw.Gi import Gtk, Gdk
from jackdaw.UI.RoutingNode import RoutingNode
from jackdaw.UI.Colors import Colors
from jackdaw.Data import data
from jackdaw.Data.ProjectData import RouterComponentData


class ChannelExistsException(Exception):
    pass


class RouterComponent(Gtk.Grid):

    def __init__(self, id: int):
        super().__init__()

        self.id = id
        self.data: RouterComponentData = data.router_components[id]

        self.header_bar = Gtk.DrawingArea()
        self.header_bar.set_size_request(0, 16)
        self.header_bar.add_events(Gdk.EventMask.BUTTON_PRESS_MASK |
                                   Gdk.EventMask.BUTTON1_MOTION_MASK |
                                   Gdk.EventMask.BUTTON_RELEASE_MASK)
        self.header_bar.connect("draw", self.on_draw_header)
        self.header_bar.connect("button-press-event", self.on_click_header)
        self.header_bar.connect("motion-notify-event", self.on_drag_header)
        self.drag_start = [0, 0]
        self.attach(self.header_bar, 0, -1, 1, 1)

        self.inputs = dict()
        self.input_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.attach(self.input_box, -1, 0, 1, 1)

        self.outputs = dict()
        self.output_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.attach(self.output_box, 1, 0, 1, 1)

    ############
    # CHANNELS #
    ############

    # If we want channels to be addable/removable at runtime,
    # then we need to save this info. A RouterComponentChannelData
    # object would then be needed.
    def add_input_channel(self, label: str):

        if label in self.inputs:
            raise ChannelExistsException(f"Input channel \"{label}\" already exists!")

        input_node = RoutingNode(label, False, label=label)
        self.inputs[label] = input_node
        self.input_box.add(input_node)
        self.show_all()

        def on_click(button: Gdk.EventButton):
            from jackdaw.UI.Router import Router
            Router.instance().on_click_routing_node(self.id, label, True)

        input_node.add_click_event(on_click)

    def add_output_channel(self, label: str):

        if label in self.outputs:
            raise ChannelExistsException(f"Output channel \"{label}\" already exists!")

        output_node = RoutingNode(label, True, label=label)
        self.outputs[label] = output_node
        self.output_box.add(output_node)
        self.show_all()

        def on_click(button: Gdk.EventButton):
            from jackdaw.UI.Router import Router
            Router.instance().on_click_routing_node(self.id, label, False)

        output_node.add_click_event(on_click)

    def get_channel_coords(self, channel: str, input: bool):
        d = self.inputs if input else self.outputs
        if channel not in d:
            raise KeyError(f"{'Input' if input else 'Output'} channel \"{channel}\" not found!")

        node: RoutingNode = d[channel]
        b = self.input_box if input else self.output_box
        x, y = node.translate_coordinates(b, *node.node_coordinates())
        return b.translate_coordinates(self, x, y)

    ###################
    # EVENT CALLBACKS #
    ###################

    def on_click_header(self, widget: Gtk.Widget, button: Gdk.EventButton):

        if button.button == Gdk.BUTTON_PRIMARY:
            self.drag_start = [button.x, button.y]
            return

        if button.button == Gdk.BUTTON_SECONDARY:
            data.router_components.pop(self.id)
            return

    def on_drag_header(self, widget: Gtk.Widget, button: Gdk.EventButton):
        parent: Gtk.Fixed = self.get_parent()
        if not isinstance(parent, Gtk.Fixed):
            raise Exception("RouterComponent not attached to fixed parent!")

        x, y = self.translate_coordinates(parent, button.x - self.drag_start[0], button.y - self.drag_start[1])
        self.data.position.value = (x, y)
        parent.move(self, x, y)

    def on_draw_header(self, widget: Gtk.Widget, context: cairo.Context):
        width = widget.get_allocated_width()
        height = widget.get_allocated_height()
        context.set_source_rgb(*Colors.router_component_header)
        context.rectangle(0, 0, width, height)
        context.fill()

    ##############
    # PROPERTIES #
    ##############

    @property
    def content(self):
        return self.get_child_at(0, 0)

    @content.setter
    def content(self, value):
        self.attach(value, 0, 0, 1, 1)
