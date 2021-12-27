from jackdaw.Session import session_close_method


class SingletonException(Exception):
    pass


class Singleton:
    _instance = None
    _instance_being_created = False

    def __init__(self):
        if not self.__class__._instance_being_created:
            raise SingletonException(
                "Tried to create instance of singleton, "
                "use class.instance() instead.")

    def on_clear_singleton_instance(self):
        pass

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance_being_created = True
            cls._instance = cls()
            cls._instance_being_created = False
        return cls._instance

    @classmethod
    def clear_instance(cls):
        if cls._instance is not None:
            cls._instance.on_clear_singleton_instance()
        cls._instance = None

    @classmethod
    def instance_exists(cls):
        return cls._instance is not None

    @staticmethod
    @session_close_method
    def on_end_session_singleton():
        for c in Singleton.__subclasses__():
            c.clear_instance()
