import gi

gi.require_version("Gtk", "3.0")

import gi.repository.Gtk as Gtk
import gi.repository.Gdk as Gdk
import gi.repository.GLib as GLib
from typing import Callable


def add_timeout(callback: Callable[[], None], time_ms: int, repeats: int = 1) -> int:
    """
    Register a delayed call via Gdk.
    :param callback: The function to call.
    :param time_ms: The timeout in milliseconds.
    :param repeats: How many times to call (0 => infinite).
    :return: The ID of the event source, returned by Gdk.threads_add_timeout.
    """

    def wrapper():
        callback()
        wrapper.calls += 1
        if repeats == 0:
            return True
        return wrapper.calls < repeats

    wrapper.calls = 0

    return Gdk.threads_add_timeout(
        GLib.PRIORITY_HIGH_IDLE, time_ms,
        lambda e: wrapper(), None)
