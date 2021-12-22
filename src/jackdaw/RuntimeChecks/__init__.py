import traceback


def must_be_called_from(method):
    for frame in traceback.extract_stack():
        if frame.name == method.__name__ and frame.filename == method.__globals__['__file__']:
            return

    raise Exception("Method called incorrectly!")
