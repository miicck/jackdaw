from typing import Type, Any, Generic, TypeVar, Callable
from abc import ABC
from collections import defaultdict
import json


class HasOnChangeListeners:

    def __init__(self):
        self._on_change_listeners = []

    def add_on_change_listener(self, listener: Callable[[], None]) -> None:
        self._on_change_listeners.append(listener)

    def invoke_on_change_listeners(self):
        for listener in self._on_change_listeners:
            listener()


class DataObject(ABC):

    def serialize(self) -> dict:
        """
        Creates a dictionary that represents a recursive serialization of my state.
        Only serializes state held in DataOBjects.
        :return: Dictionary serialization of this object.
        """
        attrs = {n: getattr(self, n) for n in dir(self)}
        return {n: attrs[n].serialize() for n in attrs if isinstance(attrs[n], DataObject)}

    def deserialize(self, data: dict) -> None:
        """
        Reconstruct this DataObject from a dictionary serialization.
        :param data: Dictionary serialization of the object to reconstruct.
        :return: None
        """
        for attr_name in data:
            getattr(self, attr_name).deserialize(data[attr_name])

    def __setattr__(self, key, value):
        if hasattr(self, key) and not isinstance(value, getattr(self, key).__class__):
            try:
                value = getattr(self, key).__class__(value)
            except:
                raise Exception("Tried to change attribute type from "
                                f"{getattr(self, key).__class__.__name__} to "
                                f"{value.__class__.__name__}")
        super().__setattr__(key, value)

    def copy(self):
        copy = self.__class__()
        copy.deserialize(self.serialize())
        return copy

    def pretty_json(self):
        return json.dumps(self.serialize(), indent=2)

    def deserialize_json(self, json_data: str):
        self.deserialize(json.loads(json_data))


KeyType = TypeVar("KeyType")
ValType = TypeVar("ValType", bound=DataObject)


class DataObjectDict(DataObject, Generic[KeyType, ValType], HasOnChangeListeners):

    def __init__(self, key_type: Type[KeyType], value_type: Type[ValType]):
        HasOnChangeListeners.__init__(self)
        """
        A DataObject version of a dictionary,
        with values that are data objects.
        :param value_type: The DataObject value type.
        """
        self._key_type = key_type
        self._value_type = value_type
        self._data = defaultdict(lambda: self._value_type())

    def serialize(self) -> dict:
        return {key: self._data[key].serialize() for key in self._data}

    def deserialize(self, data: dict) -> None:
        self._data.clear()
        for key in data:
            val = self._value_type()
            val.deserialize(data[key])
            self._data[self._key_type(key)] = val
        self.invoke_on_change_listeners()

    def __getitem__(self, key) -> ValType:
        """
        Returns the data object stored at the given key.
        Creates a new data object if it does not exist.
        :param key: The dictionary key.
        :return: The data object stored at that key (or a new data object if not present).
        """
        return self._data[key]

    def __iter__(self):
        return self._data.__iter__()


class DataObjectList(DataObject, Generic[ValType], HasOnChangeListeners):

    def __init__(self, value_type: Type[ValType]):
        HasOnChangeListeners.__init__(self)
        self._value_type = value_type
        self._data = []

    def serialize(self) -> dict:
        return {i: d.serialize() for i, d in enumerate(self._data)}

    def deserialize(self, data: dict) -> None:
        self._data.clear()
        for i in data:
            val = self._value_type()
            val.deserialize(data[i])
            self._data.append(val)
        self.invoke_on_change_listeners()

    def __getitem__(self, index: int):
        return self._data[index]

    def __iter__(self):
        return self._data.__iter__()

    def append(self, val: ValType):
        self._data.append(val)
        self.invoke_on_change_listeners()


class DataObjectSet(DataObject, Generic[ValType], HasOnChangeListeners):

    def __init__(self, value_type: Type[ValType]):
        HasOnChangeListeners.__init__(self)
        self._value_type = value_type
        self._data = set()

    def serialize(self) -> dict:
        return {i: d.serialize() for i, d in enumerate(list(self._data))}

    def deserialize(self, data: dict) -> None:
        self._data.clear()
        for i in data:
            val = self._value_type()
            val.deserialize(data[i])
            self._data.add(val)
        self.invoke_on_change_listeners()

    def add(self, val: ValType):
        if not isinstance(val, self._value_type):
            raise Exception("Tried to add object of wrong type!")
        self._data.add(val)
        self.invoke_on_change_listeners()

    def remove(self, val: ValType):
        if not isinstance(val, self._value_type):
            raise Exception("Tried to remove object of wrong type!")
        self._data.remove(val)
        self.invoke_on_change_listeners()

    def __iter__(self):
        return self._data.__iter__()

    def __len__(self):
        return len(self._data)


def is_jsonable(x):
    try:
        json.dumps(x)
        return True
    except (TypeError, OverflowError):
        return False


class NotSerializableError(Exception):
    pass


class RawDataObject(DataObject, HasOnChangeListeners):

    def __init__(self, value):
        HasOnChangeListeners.__init__(self)
        """
        Represents a bottom-level data object, storing a raw data value.
        :param value: The default value of this data object.
        """
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
