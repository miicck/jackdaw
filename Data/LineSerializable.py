from abc import ABC, abstractmethod
from typing import TypeVar, Generic, List, Callable
import os


class LineSerializable(ABC):

    @abstractmethod
    def save_to_line(self) -> str:
        """
        Save this object as a single-line string.
        :return: My data, serialized into a single line.
        """
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def load_from_line(cls, line) -> 'LineSerializable':
        """
        Creates an object from data saved
        by the save_to_line method.
        :param line: Data line to construct the object from.
        :return: Deserialized object.
        """
        raise NotImplementedError()


T = TypeVar("T", bound=LineSerializable)
collection_callback = Callable[['LineSerializableCollection'], None]


class LineSerializableCollection(ABC, Generic[T]):

    def __init__(self):
        self._data: List[T] = []
        self._change_callbacks: List[collection_callback] = []

    @property
    @abstractmethod
    def filename(self) -> str:
        raise NotImplementedError()

    def save(self) -> None:
        """
        Saves my data objects to a file,
        using one line for each.
        :return: None
        """
        os.makedirs(os.path.dirname(self.filename), exist_ok=True)
        with open(self.filename, "w") as f:
            for n in self._data:
                f.write(n.save_to_line().strip() + "\n")

        # No data => get rid of data file
        if len(self._data) == 0:
            os.remove(self.filename)

    def load(self, loader: Callable[[str], T]) -> None:
        """
        Load my data from a file, by creating
        a data object from each line in the file.
        :return: None
        """
        self._data = []
        if os.path.isfile(self.filename):
            with open(self.filename, "r") as f:
                for line in f:
                    self._data.append(loader(line))

    def add(self, data_obj: T) -> None:
        """
        Adds a data object to this collection.
        :param data_obj: The object to add.
        :return: None
        """
        self._data.append(data_obj)
        self.on_change()

    def remove(self, data_obj: T) -> None:
        """
        Removes a data object form this collection.
        :param data_obj: The object to remove.
        :return: None
        """
        if data_obj not in self._data:
            raise Exception("Data object to remove not found in collection!")
        self._data.remove(data_obj)
        self.on_change()

    def on_change(self):
        """
        Called whenever my data changes.
        :return: None
        """
        for callback in self._change_callbacks:
            callback(self)
        self.save()

    def add_change_listener(self, callback: collection_callback) -> None:
        """
        Add a listener that is called when my data changes.
        :param callback: The listener.
        :return: None
        """
        self._change_callbacks.append(callback)

    ##############
    # PROPERTIES #
    ##############

    @property
    def data(self) -> List[T]:
        """
        :return: A list of data objects in this collection.
        """
        return [d for d in self._data]
