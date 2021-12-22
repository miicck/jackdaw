import traceback


class CallStructureException(Exception):
    pass


def must_be_called_from(method):
    for frame in traceback.extract_stack():
        if frame.name == method.__name__ and frame.filename == method.__globals__['__file__']:
            return

    raise CallStructureException("Method called incorrectly!")
