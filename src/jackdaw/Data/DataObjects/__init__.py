from typing import Type, Any, Generic, TypeVar
from abc import ABC
from collections import defaultdict
import json


class DataObject(ABC):
    """
    An object that allows deep-copy, recursive serialization of DataObject fields.
    """

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

    def pretty_json(self):
        return json.dumps(self.serialize(), indent=2)

    def deserialize_json(self, json_data: str):
        self.deserialize(json.loads(json_data))


KeyType = TypeVar("KeyType")
ValType = TypeVar("ValType", bound=DataObject)


class DataObjectDict(DataObject, Generic[KeyType, ValType]):

    def __init__(self, key_type: Type[KeyType], value_type: Type[ValType]):
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

    def __getitem__(self, key) -> ValType:
        """
        Returns the data object stored at the given key.
        Creates a new data object if it does not exist.
        :param key: The dictionary key.
        :return: The data object stored at that key (or a new data object if not present).
        """
        return self._data[key]


def is_jsonable(x):
    try:
        json.dumps(x)
        return True
    except (TypeError, OverflowError):
        return False


class NotSerializableError(Exception):
    pass


class RawDataObject(DataObject):

    def __init__(self, value):
        """
        Represents a bottom-level data object, storing a raw data value.
        :param value: The default value of this data object.
        """
        if not is_jsonable(value):
            raise NotSerializableError(f"The provided value is of non-serializable type: "
                                       f"{value.__class__.__name__}")
        self.value = value

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
