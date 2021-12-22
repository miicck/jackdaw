_close_methods = []


def session_close_method(close_method: callable):
    _close_methods.append(close_method)
    return close_method


def call_session_close_methods():
    for m in _close_methods:
        m()
