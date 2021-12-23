import cairo
from jackdaw.Gi import Gtk, Gdk
from jackdaw.RuntimeChecks import must_be_called_from
from jackdaw.UI.Colors import Colors
from jackdaw.Data import data
from jackdaw.Data.ProjectData import RouterComponentData
from jackdaw.UI.RouterComponent import RouterComponent
from jackdaw.Utils.Singleton import Singleton

# This is needed so we can enumerate RouterComponent subclasses
import jackdaw.UI.RouterComponents


class Router(Gtk.Window, Singleton):

    def __init__(self):
        must_be_called_from(Router.instance)
        super().__init__(title="Router")

        self.set_default_size(800, 800)
        data.router_components.add_on_change_listener(self.on_data_change)

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
        self.surface.add(background)

        self.connect("destroy", lambda e: Router.clear_instance())
        self.on_data_change()
        self.show_all()

    def on_clear_singleton_instance(self):
        self.destroy()

    def on_data_change(self):

        # Remove old components
        for c in self.surface.get_children():
            if isinstance(c, RouterComponent):
                c.destroy()

        # Get all component types
        component_types = dict()
        for c in RouterComponent.__subclasses__():
            component_types[c.__name__] = c

        for comp_data in data.router_components:

            comp_type = comp_data.type.value
            position = comp_data.position.value

            if comp_type not in component_types:
                raise Exception(f"Unknown router component type: {comp_type}\n"
                                f"Is not one of {list(component_types)}")

            component = component_types[comp_type]()
            component.data = comp_data
            self.surface.put(component, position[0], position[1])

        self.surface.show_all()

    def add_track_signal(self, x, y):
        new_data = RouterComponentData()
        new_data.type.value = "TrackSignal"
        new_data.position.value = (x, y)
        data.router_components.add(new_data)

    ###################
    # EVENT CALLBACKS #
    ###################

    def on_draw_background(self, widget: Gtk.Widget, context: cairo.Context):
        width = widget.get_allocated_width()
        height = widget.get_allocated_height()
        context.set_source_rgb(*Colors.background_black_key)
        context.rectangle(0, 0, width, height)
        context.fill()

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
