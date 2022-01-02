import multiprocessing as mp
from typing import List, Union, Dict, Set, Tuple
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

        self._chunk_index = mp.Queue()
        self._chunk_index.put(0)

        self._chunks_to_render = mp.Queue()
        self._chunks_to_render.put(10)

        self._parents = mp.Queue()
        self._parents.put(dict())

        self.results = mp.Queue()
        self.results.put(dict())

        self.node_types = mp.Queue()
        self.node_types.put(dict())

    def next(self) -> Union[Tuple[Chunk, Node], None]:

        # Order of nodes to render/index of node to render
        order = self.node_order
        index = self._node_index.get()

        # Index beyond order array => we're done
        if index >= len(order):
            self._node_index.put(index)
            return None

        if index == len(order) - 1:  # Last node of the chunk

            # Work out how many chunks we need to render
            chunk_limit = self._chunks_to_render.get()
            self._chunks_to_render.put(chunk_limit)

            # Get the chunk we're currently rendering
            chunk = self._chunk_index.get()

            if chunk + 1 >= chunk_limit:
                # All chunks rendered
                self._chunk_index.put(chunk)
                self._node_index.put(index + 1)
                return chunk, order[index]

            # Last node of this chunk, increment
            # the chunk and go back no node index 0
            self._chunk_index.put(chunk + 1)
            self._node_index.put(0)
            return chunk, order[index]

        # Increment the node index
        chunk = self._chunk_index.get()
        self._chunk_index.put(chunk)
        self._node_index.put(index + 1)
        return chunk, order[index]

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
