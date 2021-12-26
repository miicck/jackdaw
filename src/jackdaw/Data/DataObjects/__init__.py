from typing import Type, Any, Generic, TypeVar, Callable
from abc import ABC
import json


class TypeMismatchException(Exception):
    """
    Thrown when types don't match at runtime.
    """
    pass


class NotSerializableError(Exception):
    """
    Thrown when a DataObject is given a non-serializable type.
    """
    pass


class HasOnChangeListeners:

    def __init__(self):
        """
        A class that allows the adding and
        calling of "on change" listeners.
        """
        self._on_change_listeners = []

    def add_on_change_listener(self, listener: Callable[[], None]) -> None:
        """
        Add a listener to be invoked on a change.
        :param listener: The listener to call just after a change happens.
        :return: None
        """
        self._on_change_listeners.append(listener)

    def invoke_on_change_listeners(self) -> None:
        """
        Call all of the currently-registered
        "on change" listeners.
        :return: None
        """
        for listener in self._on_change_listeners:
            listener()


class DataObject(ABC):

    def serialize(self) -> dict:
        """
        Creates a dictionary that represents a recursive serialization of my state.
        Only serializes state held in DataOBjects.
        :return: Dictionary serialization of this object.
        """
        data = dict()
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if isinstance(attr, DataObject) and attr is not self:
                data[attr_name] = attr.serialize()
        return data

    def deserialize(self, data: dict) -> None:
        """
        Reconstruct this DataObject from a dictionary serialization.
        :param data: Dictionary serialization of the object to reconstruct.
        :return: None
        """
        for attr_name in data:
            getattr(self, attr_name).deserialize(data[attr_name])

    def __setattr__(self, key, value):
        """
        Perform runtime type checking/casting when setting values.
        :param key: attribute name to set
        :param value: value to set it to
        :return: None
        :raise TypeMismatchException if types are incompatible
        """
        if hasattr(self, key):
            target_type = getattr(self, key).__class__
            value = DataObject.try_cast(value, target_type)

        super().__setattr__(key, value)

    def copy(self) -> 'DataObject':
        """
        Copy via serialization/deserialization.
        :return: A deep-data copy of this data object.
        """
        copy = self.__class__()
        copy.deserialize(self.serialize())
        return copy

    ########
    # JSON #
    ########

    def get_pretty_json_string(self):
        return json.dumps(self.serialize(), indent=2)

    def write_pretty_json_file(self, f):
        json.dump(self.serialize(), f, indent=2)

    def deserialize_from_json_str(self, json_data: str):
        self.deserialize(json.loads(json_data))

    def deserialize_from_json_file(self, f):
        self.deserialize(json.load(f))

    ################
    # STATIC STUFF #
    ################

    @staticmethod
    def try_cast(value, type_to: Type):
        """
        Attempt to cast a value to the given type.
        :param value: Value to cast.
        :param type_to: Value to cast to.
        :return: casted value.
        :raise TypeMismatchException if types are incompatible
        """

        # Value is of correct type, just return it
        if isinstance(value, type_to):
            return value

        # Value can be cast to the correct type
        if DataObject.allowed_cast(value.__class__, type_to):
            return type_to(value)

        raise TypeMismatchException(
            f"Tried to cast a value from type "
            f"'{value.__class__.__name__}' "
            f"to type '{type_to.__name__}'")

    @staticmethod
    def allowed_cast(type_from: Type, type_to: Type):
        if type_from is int and type_to is float:
            return True
        if type_from is list and type_to is tuple:
            return True
        return False


KeyType = TypeVar("KeyType")
ValType = TypeVar("ValType", bound=DataObject)


class DataObjectDict(DataObject, Generic[KeyType, ValType], HasOnChangeListeners):

    def __init__(self, key_type: Type[KeyType], value_type: Type[ValType]):
        """
        A DataObject version of a dictionary,
        with values that are data objects.
        :param value_type: The DataObject value type.
        """
        HasOnChangeListeners.__init__(self)
        self._key_type = key_type
        self._value_type = value_type
        self._data = dict()

    def __getitem__(self, key) -> ValType:
        """
        Returns the data object stored at the given key.
        :param key: The dictionary key.
        :return: The data object stored at that key.
        :raise KeyError if key not present.
        """
        if not isinstance(key, self._key_type):
            raise TypeMismatchException(
                f"Tried to use a key of the wrong type expected "
                f"{self._key_type.__name__}, got {key.__class__.__name__}.")

        if key not in self._data:
            raise KeyError(f"Key not found in data object dictionary: \"{key}\"")

        return self._data[key]

    def __setitem__(self, key, value):
        if not isinstance(key, self._key_type):
            raise TypeMismatchException(
                f"Tried to use a key of the wrong type expected "
                f"{self._key_type.__name__}, got {key.__class__.__name__}.")

        if not isinstance(value, self._value_type):
            raise TypeMismatchException(
                f"Tried to use a value of the wrong type expected "
                f"{self._value_type.__name__}, got {value.__class__.__name__}.")

        if key in self._data:
            if value != self._data[key]:
                raise Exception(f"Tried to overwrite value at key: \"{key}\"")

        self._data[key] = value
        self.invoke_on_change_listeners()

    def __iter__(self):
        return self._data.__iter__()

    def __len__(self):
        return len(self._data)

    def __contains__(self, item: KeyType):
        if not isinstance(item, self._key_type):
            raise TypeMismatchException(
                f"Tried to use a key of the wrong type expected "
                f"{self._key_type.__name__}, got {item.__class__.__name__}.")
        return item in self._data

    def serialize(self) -> dict:
        return {key: self._data[key].serialize() for key in self._data}

    def deserialize(self, data: dict) -> None:
        self._data.clear()
        for key in data:
            val = self._value_type()
            val.deserialize(data[key])
            self._data[self._key_type(key)] = val
        self.invoke_on_change_listeners()

    def get_unique_key(self) -> KeyType:
        """
        Get a dictionary key that is not yet used.
        :return: A unique key.
        """
        if self._key_type == int:
            n = 0
            while n in self._data:
                n += 1
            return n

        raise Exception(f"Can't generate unique key for key type {self._key_type.__name__}")

    def pop(self, key: KeyType):
        """
        Pop the data object at the given key from the dictionary.
        :param key: The key to pop.
        :return: The value popped.
        """
        if key not in self._data:
            raise KeyError(f"Key not found in data object dictionary: \"{key}\"")
        data = self._data.pop(key)
        self.invoke_on_change_listeners()
        return data


class DataObjectList(DataObject, Generic[ValType], HasOnChangeListeners):

    def __init__(self, value_type: Type[ValType]):
        """
        A data object version of a list.
        :param value_type: The value type to be stored in the list.
        """
        HasOnChangeListeners.__init__(self)
        self._value_type = value_type
        self._data = []

    def __getitem__(self, index: int):
        return self._data[index]

    def __iter__(self):
        return self._data.__iter__()

    def append(self, val: ValType) -> None:
        """
        Append a value to the end of the list.
        :param val: Value to append.
        :return: None.
        """
        val = DataObject.try_cast(val, self._value_type)
        self._data.append(val)
        self.invoke_on_change_listeners()

    def serialize(self) -> dict:
        return {i: d.serialize() for i, d in enumerate(self._data)}

    def deserialize(self, data: dict) -> None:
        self._data.clear()
        for i in data:
            val = self._value_type()
            val.deserialize(data[i])
            self._data.append(val)
        self.invoke_on_change_listeners()


class DataObjectSet(DataObject, Generic[ValType], HasOnChangeListeners):

    def __init__(self, value_type: Type[ValType]):
        """
        A DataObject version of a set.
        :param value_type: The type of values in the set.
        """
        HasOnChangeListeners.__init__(self)
        self._value_type = value_type
        self._data = set()

    def __iter__(self):
        return self._data.__iter__()

    def __contains__(self, item):
        return item in self._data

    def __len__(self):
        return len(self._data)

    def add(self, val: ValType):
        """
        Add a DataObject to the set.
        :param val: Value to add.
        :return: None
        """
        val = DataObject.try_cast(val, self._value_type)
        self._data.add(val)
        self.invoke_on_change_listeners()

    def remove(self, val: ValType):
        """
        Remove a DataObject from the set.
        :param val: Value to remove.
        :return: None
        """
        val = DataObject.try_cast(val, self._value_type)
        self._data.remove(val)
        self.invoke_on_change_listeners()

    def serialize(self) -> dict:
        return {i: d.serialize() for i, d in enumerate(list(self._data))}

    def deserialize(self, data: dict) -> None:
        self._data.clear()
        for i in data:
            val = self._value_type()
            val.deserialize(data[i])
            self._data.add(val)
        self.invoke_on_change_listeners()


def is_jsonable(x):
    """
    :param x: Value to test.
    :return: True if value can be JSON-serialized.
    """
    try:
        json.dumps(x)
        return True
    except (TypeError, OverflowError):
        return False


class RawDataObject(DataObject, HasOnChangeListeners):

    def __init__(self, value):
        """
        Represents a bottom-level data object, storing
        a raw, serializable data value.
        :param value: The default value of this data object.
        """
        HasOnChangeListeners.__init__(self)
        if not is_jsonable(value):
            raise NotSerializableError(f"The provided value is of non-serializable type: "
                                       f"{value.__class__.__name__}")
        self._value = value  # Should on change be invoked here?

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self._value = new_value
        self.invoke_on_change_listeners()

    def serialize(self) -> Any:
        """
        The serialization of a raw data value, is just the data value.
        :return: The value.
        """
        return self.value

    def deserialize(self, data: Any) -> None:
        """
        Sets self.value to data. This is because a raw data object is
        it's own serialization.
        :param data: new value
        :return: None
        """
        self.value = data
