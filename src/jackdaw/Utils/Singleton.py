from jackdaw.Session import session_close_method


class SingletonException(Exception):
    pass


class Singleton:

    def __init__(self):

        if not hasattr(self.__class__, Singleton.SINGLETON_CREATION_FLAG) or \
                not getattr(self.__class__, Singleton.SINGLETON_CREATION_FLAG):
            raise SingletonException(
                "Tried to create instance of singleton, "
                "use class.instance() instead.")

    def on_clear_singleton_instance(self):
        pass

    @classmethod
    def instance(cls):

        # Check for existence of instance
        if hasattr(cls, Singleton.SINGLETON_INSTANCE_NAME):
            attr = getattr(cls, Singleton.SINGLETON_INSTANCE_NAME)
            if attr is not None:
                return attr

        # Create instance
        setattr(cls, Singleton.SINGLETON_CREATION_FLAG, True)
        setattr(cls, Singleton.SINGLETON_INSTANCE_NAME, cls())
        setattr(cls, Singleton.SINGLETON_CREATION_FLAG, False)
        return getattr(cls, Singleton.SINGLETON_INSTANCE_NAME)

    @classmethod
    def clear_instance(cls):
        cls.instance().on_clear_singleton_instance()
        setattr(cls, Singleton.SINGLETON_INSTANCE_NAME, None)

    @classmethod
    def instance_exists(cls):
        return hasattr(cls, Singleton.SINGLETON_INSTANCE_NAME) and \
               getattr(cls, Singleton.SINGLETON_INSTANCE_NAME) is not None

    @staticmethod
    @session_close_method
    def on_end_session_singleton():
        for c in Singleton.__subclasses__():
            c.clear_instance()

    SINGLETON_INSTANCE_NAME = "_singleton_instance"
    SINGLETON_CREATION_FLAG = "_creating_singleton_instance"
