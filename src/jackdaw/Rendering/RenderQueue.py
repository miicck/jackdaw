import multiprocessing as mp
from typing import List, Union, Dict, Set
from jackdaw.Rendering.Typedefs import *
from jackdaw.Rendering.Signal import Signal


# Contains process-safe information
# relating to the rendering queue.
class RenderQueue:

    def __init__(self):
        self.kill_switch = mp.Queue()
        self.kill_switch.put(False)

        self._queue = mp.Queue()
        self._queue.put([])

        self.results = mp.Queue()
        self.results.put(dict())

        self._parents = mp.Queue()
        self._parents.put(dict())

        self.node_types = mp.Queue()
        self.node_types.put(dict())

    @property
    def queue(self) -> List[Node]:
        queue = self._queue.get()
        self._queue.put(queue)
        return queue

    @queue.setter
    def queue(self, queue: List[Node]):
        self._queue.get()
        self._queue.put(queue)

    def dequeue(self) -> Union[Node, None]:
        queue: List[Node] = self._queue.get()
        node = None if len(queue) == 0 else queue.pop(0)
        self._queue.put(queue)
        return node

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
        killed = self.kill_switch.get()
        self.kill_switch.put(killed)
        return killed

    @killed.setter
    def killed(self, val: bool):
        self.kill_switch.get()
        self.kill_switch.put(val)
