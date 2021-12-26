import cairo
from jackdaw.Gi import Gtk, Gdk
from jackdaw.UI.Colors import Colors
from jackdaw.Data import data
from jackdaw.Data.ProjectData import RouterComponentData, RouterRouteData
from jackdaw.UI.RouterComponent import RouterComponent
from jackdaw.Utils.Singleton import Singleton
from typing import Iterable

# This is needed so we can enumerate RouterComponent subclasses
import jackdaw.UI.RouterComponents


class Router(Gtk.Window, Singleton):

    def __init__(self):
        super().__init__(title="Router")

        self.set_default_size(800, 800)
        self._current_route_start = None
        data.router_components.add_on_change_listener(self.on_components_change)
        data.routes.add_on_change_listener(self.on_routes_change)

        scroll_area = Gtk.ScrolledWindow()
        self.add(scroll_area)

        self.surface = Gtk.Fixed()
        self.surface.set_size_request(8192, 8192)
        scroll_area.add(self.surface)

        background = Gtk.DrawingArea()
        background.set_size_request(8192, 8192)
        background.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        background.connect("draw", self.on_draw_background)
        background.connect("button-press-event", self.on_click_background)
        self.background = background
        self.surface.add(background)

        self.connect("destroy", lambda e: Router.clear_instance())
        self.on_components_change()
        self.show_all()

    def add_track_signal(self, x, y):
        new_data = RouterComponentData()
        new_data.type.value = "TrackSignal"
        new_data.position.value = (x, y)
        key = data.router_components.get_unique_key()
        data.router_components[key] = new_data

    def get_channel_coords(self, component_id: int, channel: str, input: bool):

        component = None
        for c in self.components:
            if c.id == component_id:
                component = c
                break

        if component is None:
            raise Exception(f"Could not find the component with id {component_id}.")

        x, y = component.get_channel_coords(channel, input)
        x, y = component.translate_coordinates(self.surface, x, y)
        return x, y

    ##############
    # PROPERTIES #
    ##############

    @property
    def components(self) -> Iterable[RouterComponent]:
        for c in self.surface.get_children():
            if isinstance(c, RouterComponent):
                yield c

    ###################
    # EVENT CALLBACKS #
    ###################

    def on_clear_singleton_instance(self):
        self.destroy()

    def on_components_change(self):

        # Remove old components
        for c in self.components:
            c.destroy()

        # Get all component types
        component_types = dict()
        for c in RouterComponent.__subclasses__():
            component_types[c.__name__] = c

        for comp_id in data.router_components:
            comp_data = data.router_components[comp_id]

            comp_type = comp_data.type.value
            position = comp_data.position.value

            if comp_type not in component_types:
                raise Exception(f"Unknown router component type: {comp_type}\n"
                                f"Is not one of {list(component_types)}")

            component = component_types[comp_type](comp_id)
            self.surface.put(component, position[0], position[1])

        def route_valid(r: RouterRouteData):
            return r.from_component.value in data.router_components and \
                   r.to_component.value in data.router_components

        # Remove invalid routes
        invalid_routes = [r for r in data.routes if not route_valid(r)]
        for r in invalid_routes:
            data.routes.remove(r)

        self.surface.show_all()

    def on_routes_change(self):
        self.background.queue_draw()

    def on_click_routing_node(self, component_id: int, channel: str, input: bool):

        if not input:
            # Start a route from an output channel
            self._current_route_start = [component_id, channel]

        elif self._current_route_start is not None:
            # End a route at an input channel

            # Check if route already exists, if so, delete it
            for route in data.routes:
                if route.from_component.value == self._current_route_start[0] and \
                        route.from_channel.value == self._current_route_start[1] and \
                        route.to_component.value == component_id and \
                        route.to_channel.value == channel:
                    data.routes.remove(route)
                    self._current_route_start = None
                    return

            # Create new route
            route = RouterRouteData()
            route.from_component.value = self._current_route_start[0]
            route.from_channel.value = self._current_route_start[1]
            route.to_component.value = component_id
            route.to_channel.value = channel
            data.routes.add(route)
            self._current_route_start = None

    def on_draw_background(self, widget: Gtk.Widget, context: cairo.Context):
        width = widget.get_allocated_width()
        height = widget.get_allocated_height()
        context.set_source_rgb(*Colors.background_black_key)
        context.rectangle(0, 0, width, height)
        context.fill()

        # Draw connections
        context.set_source_rgb(0.0, 0.0, 0.0)
        for route in data.routes:
            context.move_to(*self.get_channel_coords(route.from_component.value, route.from_channel.value, False))
            context.line_to(*self.get_channel_coords(route.to_component.value, route.to_channel.value, True))
        context.stroke()

    def on_click_background(self, area: Gtk.Widget, button: Gdk.EventButton):

        if button.button == Gdk.BUTTON_SECONDARY:

            # Create context menu
            context_options = {
                "Add: Track signal": lambda a, b, x=button.x, y=button.y: self.add_track_signal(x, y)
            }

            menu = Gtk.Menu()
            for i, label in enumerate(context_options):
                entry = Gtk.MenuItem(label=label)
                entry.connect("button-press-event", context_options[label])
                menu.attach(entry, 0, 1, i, i + 1)
            menu.show_all()
            menu.popup(None, None, None, None, button.button, button.time)
