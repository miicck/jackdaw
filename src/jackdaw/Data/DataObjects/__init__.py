from typing import Type
from abc import ABC


class DataObject(ABC):

    def serialize(self) -> dict:

        data = dict()

        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if isinstance(attr, DataObject):
                data[attr_name] = attr.serialize()

        return {self.__class__.__name__: data}

    def pretty_json(self):
        import json
        return json.dumps(self.serialize(), indent=2)


class DataObjectDict(DataObject):

    def __init__(self, value_type: Type[DataObject]):
        self._type = value_type
        self._data = dict()

    def serialize(self) -> dict:
        data = {key: self._data[key].serialize() for key in self._data}
        return {self.__class__.__name__: data}

    def __getitem__(self, item):
        if item not in self._data:
            self._data[item] = self._type()

        return self._data[item]


class RawDataObject(DataObject):

    def __init__(self, value):
        self.value = value

    def serialize(self) -> dict:
        return {"value": self.value}
