import cairo
from jackdaw.Session import session_close_method
from jackdaw.Gi import Gtk, Gdk
from jackdaw.UI.RouterComponents.TrackSignal import TrackSignal
from jackdaw.RuntimeChecks import must_be_called_from
from jackdaw.UI.Colors import Colors
from jackdaw.Data.RouterData import RouterData
from jackdaw.Data.RouterComponentData import RouterComponentData
from jackdaw.UI.RouterComponent import RouterComponent

# This is needed so we can enumerate RouterComponent subclasses
from jackdaw.UI.RouterComponents import *


class Router(Gtk.Window):

    def __init__(self):
        must_be_called_from(Router.open)
        super().__init__(title="Router")
        self.set_default_size(800, 800)
        self.data = RouterData.get()
        self.data.add_change_listener(self.on_data_change)

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

        self.connect("destroy", lambda e: Router.close())
        self.on_data_change(self.data)
        self.show_all()

    def on_data_change(self, data: RouterData):

        # Get all component types
        component_types = dict()
        for c in RouterComponent.__subclasses__():
            component_types[c.__name__] = c

        for comp_data in data.components:

            if comp_data.component_type not in component_types:
                raise Exception(f"Unknown router component type: {comp_data.component_type}")

            component = component_types[comp_data.component_type]()
            self.surface.put(component, comp_data.position[0], comp_data.position[1])

        self.surface.show_all()

    def add_track_signal(self, x, y):
        self.data.add(RouterComponentData("TrackSignal", (x, y)))

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

    ################
    # STATIC STUFF #
    ################

    _open_router: 'Router' = None

    @staticmethod
    def open():
        if Router._open_router is None:
            Router._open_router = Router()
        Router._open_router.present()
        return Router._open_router

    @staticmethod
    @session_close_method
    def close():
        if Router._open_router is None:
            return
        Router._open_router.destroy()
        Router._open_router = None
