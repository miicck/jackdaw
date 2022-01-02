import multiprocessing as mp
from typing import List, Union, Dict, Set
from jackdaw.Rendering.Typedefs import *
from jackdaw.Utils.Singleton import Singleton


# Contains process-safe information
# relating to the rendering queue.
class RenderQueue(Singleton):

    def __init__(self):
        Singleton.__init__(self)
        self._kill_switch = mp.Queue()
        self._kill_switch.put(False)

        self._node_order = mp.Queue()
        self._node_order.put([])

        self._node_index = mp.Queue()
        self._node_index.put(0)

        self._parents = mp.Queue()
        self._parents.put(dict())

        self.results = mp.Queue()
        self.results.put(dict())

        self.node_types = mp.Queue()
        self.node_types.put(dict())

    def next(self) -> Union[Node, None]:
        order = self.node_order
        index = self._node_index.get()

        if index >= len(order):
            self._node_index.put(index)
            return None
        else:
            self._node_index.put(index + 1)
            return order[index]

    @property
    def node_order(self) -> List[Node]:
        queue = self._node_order.get()
        self._node_order.put(queue)
        return queue

    @node_order.setter
    def node_order(self, queue: List[Node]):
        self._node_order.get()
        self._node_index.get()
        self._node_order.put(queue)
        self._node_index.put(0)

    @property
    def remaining(self) -> List[Node]:
        order: List[Node] = self._node_order.get()
        self._node_order.put(order)
        index = self._node_index.get()
        self._node_index.put(index)
        return order[index:]

    @property
    def done(self) -> bool:
        return len(self.remaining) == 0

    @property
    def parents(self) -> Dict[Node, Set[Node]]:
        par = self._parents.get()
        self._parents.put(par)
        return par

    @parents.setter
    def parents(self, par: Dict[Node, Set[Node]]):
        self._parents.get()
        self._parents.put(par)

    @property
    def killed(self):
        killed = self._kill_switch.get()
        self._kill_switch.put(killed)
        return killed

    @killed.setter
    def killed(self, val: bool):
        self._kill_switch.get()
        self._kill_switch.put(val)
