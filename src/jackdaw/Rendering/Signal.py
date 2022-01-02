import numpy as np
from typing import Dict, Union, Iterable


class Signal:

    def __init__(self):
        self._data: Dict[int, np.ndarray] = dict()

    def __getitem__(self, item) -> Union[np.ndarray]:
        assert isinstance(item, int)
        if item in self._data:
            return self._data[item]
        return np.zeros(self.samples)

    def __setitem__(self, key, value):
        assert isinstance(key, int)
        assert isinstance(value, np.ndarray) or value is None
        if value is None:
            if key in self._data:
                self._data.pop(key)
            return
        self._data[key] = value

    def __iter__(self):
        return self._data.__iter__()

    def __contains__(self, item):
        assert isinstance(item, int)
        return item in self._data

    def __add__(self, other: 'Signal') -> 'Signal':
        assert isinstance(other, Signal)
        result = Signal()
        for k in self:
            result[k] = self[k].copy()
        for k in other:
            if k in result:
                result[k] += other[k]
            else:
                result[k] = other[k].copy()
        return result

    def __radd__(self, other: 'Signal'):
        assert isinstance(other, Signal)
        return self + other

    @property
    def samples(self) -> int:
        for channel in self._data:
            return len(self._data[channel])
        return 0

    @staticmethod
    def sum(signals: Iterable['Signal']) -> 'Signal':
        result = Signal()
        for s in signals:
            if s is not None:
                result += s
        return result
