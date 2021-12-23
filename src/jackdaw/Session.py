_close_methods = []


def session_close_method(close_method: callable) -> callable:
    """
    A method that will be automatically
    called when the session closes.
    :param close_method: Method to call on session close.
    :return: The decorated method that will be called on session close.
    """
    _close_methods.append(close_method)
    return close_method


def call_session_close_methods() -> None:
    """
    Call all of the methods decorated with @session_close_method.
    :return: None
    """
    for m in _close_methods:
        m()
