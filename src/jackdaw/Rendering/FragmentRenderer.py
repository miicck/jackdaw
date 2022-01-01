import time

from jackdaw.Data import data
from jackdaw.Utils.Singleton import Singleton
import numpy as np
import multiprocessing as mp
from typing import Set, Tuple, NamedTuple, Dict, Type, Union, List
from collections import namedtuple
from queue import LifoQueue


# A node is a pair (component id, node name)
class Node(NamedTuple):
    id: int
    node: str


# A route connects two nodes
class Route(NamedTuple):
    from_node: Node
    to_node: Node


class FragmentRenderer(Singleton):

    def __init__(self):
        Singleton.__init__(self)

        # The current set of routes/output nodes
        self._routes: Set[Route] = set()
        self._renderers: Dict[Node, NodeRenderer] = dict()

        data.routes.add_on_change_listener(self.update_routes)
        self.update_routes()

    def get_renderer(self, node: Node):
        return self._renderers[node]

    def render_master(self, start: int, samples: int):
        return np.zeros(samples), np.zeros(samples)

    def update_routes(self):
        # Get the new set of routes from data
        new_routes: Set[Route] = {Route(
            Node(r.from_component.value, r.from_node.value),
            Node(r.to_component.value, r.to_node.value)
        ) for r in data.routes}

        # Work out added/removed routes
        added_routes = new_routes - self._routes
        removed_routes = self._routes - new_routes

        # Get the new set of output nodes from the new routes
        new_output_nodes = {r.from_node for r in new_routes}
        added_output_nodes = new_output_nodes - self.output_nodes
        removed_output_nodes = self.output_nodes - new_output_nodes

        # Get the new set of input nodes from the new routes
        new_input_nodes = {r.to_node for r in new_routes}
        added_input_nodes = new_input_nodes - self.input_nodes
        removed_input_nodes = self.input_nodes - new_input_nodes

        # Update current sets
        self._routes = new_routes

        # Call update functions
        for n in removed_input_nodes:
            self.remove_node(n)
        for n in added_input_nodes:
            self.add_node(n, InputRenderer)

        for n in removed_output_nodes:
            self.remove_node(n)
        for n in added_output_nodes:
            self.add_node(n, OutputRenderer)

        for r in removed_routes:
            self.remove_route(r)
        for r in added_routes:
            self.add_route(r)

    def add_node(self, node: Node, render_type: Type['NodeRenderer']):
        self._renderers[node] = render_type(node, self)

    def remove_node(self, node: Node):
        renderer = self._renderers.pop(node)
        assert renderer.node == node
        renderer.destroy()

    def add_route(self, route: Route):
        self.invalidate_downstream(route.to_node.id)

    def remove_route(self, route: Route):
        self.invalidate_downstream(route.to_node.id)

    def downstream_components(self, comp_id: int) -> Set[int]:

        # The components awaiting expansion/
        # those that have been expanded
        open_set = {comp_id}
        closed_set = set()

        while len(open_set) > 0:

            # The component we're currently expanding downstream
            current = open_set.pop()
            closed_set.add(current)

            # Add all unexplored components that are
            # immediately downstream from current
            for route in self._routes:
                if route.from_node.id == current:
                    if route.to_node.id not in closed_set:
                        open_set.add(route.to_node.id)

        return closed_set

    def invalidate_downstream(self, comp_id: int):

        # Invalidate downstream node renderers
        for comp_id in self.downstream_components(comp_id):
            for node in self._renderers:
                if node.id == comp_id:
                    self._renderers[node].invalidate()

    ##############
    # Properties #
    ##############

    @property
    def routes(self) -> Set[Route]:
        return self._routes

    @property
    def output_nodes(self) -> Set[Node]:
        return {n for n in self._renderers if isinstance(self._renderers[n], OutputRenderer)}

    @property
    def input_nodes(self) -> Set[Node]:
        return {n for n in self._renderers if isinstance(self._renderers[n], InputRenderer)}


class RenderBlock(NamedTuple):
    node: Node
    block: int
    channel: int


class RenderQueue:

    def __init__(self):
        self.to_render: List[RenderBlock] = []
        self.rendered: Dict[RenderBlock, np.ndarray] = dict()


render_processes = []


def start_render_queue():
    global render_processes
    render_queue = mp.Queue()
    render_queue.put(RenderQueue())

    for n in range(mp.cpu_count()):
        args = (render_queue,)
        p = mp.Process(target=render_worker, args=args)
        p.start()
        render_processes.append(p)


def render_worker(render_queue: mp.Queue):
    q: RenderQueue = render_queue.get()
    if len(q.to_render) == 0:
        # Nothing to render
        render_queue.put(q)
        return

    # Get the last RenderBlock queued
    # (last because this is the least likely to have dependencies)
    block = q.to_render.pop(-1)


# Identifier of a single block of rendered signal
class RenderBlock(NamedTuple):
    block: int
    channel: int


RenderResult = Union[None, np.array]


class RenderQueue:

    def __init__(self):
        self.to_render: List[RenderBlock] = []
        self.rendered: Dict[RenderBlock, np.ndarray] = dict()

    def try_pop(self, block: RenderBlock):
        if block in self.rendered:
            return self.rendered.pop(block)
        return None


class NodeRenderer:
    BLOCK_SIZE = 256

    def __init__(self, node: Node, frag_renderer: FragmentRenderer):
        self.node = node
        self.frag_renderer = frag_renderer

        # Queue of blocks to render
        self.render_queue = mp.Queue()
        self.render_queue.put(RenderQueue())

        # Will contain rendered blocks
        self.rendered: Dict[RenderBlock, np.ndarray] = dict()

        print(f"{self.__class__.__name__} {self.node} created")

    def get_block(self, block: RenderBlock) -> Union[np.ndarray, None]:

        # Return previously-rendered block
        if block in self.rendered:
            return self.rendered[block]

        # Attempt to get rendered block from queue
        rq: RenderQueue = self.render_queue.get()
        render = rq.try_pop(block)
        if render is None:
            # Ensure that rendering of
            # this block is queued
            if block not in rq.to_render:
                rq.to_render.add(block)
        else:
            # Render has succeeded
            # Save to local rendered blocks
            self.rendered[block] = render

        self.render_queue.put(rq)
        return render

    def invalidate(self):
        print(f"{self.__class__.__name__} {self.node} invalidated")
        self.on_invalidate()

    def destroy(self):
        print(f"{self.__class__.__name__} {self.node} destroyed")

    def on_invalidate(self):
        pass


class OutputRenderer(NodeRenderer):

    def __init__(self, node: Node, frag_renderer: FragmentRenderer):
        super().__init__(node, frag_renderer)
        self.inputs: Dict[Node, InputRenderer] = dict()

    def on_invalidate(self):

        # Get all the (connected) inputs to my component
        self.inputs = dict()
        for r in self.frag_renderer.routes:
            if self.node.id == r.to_node.id:
                input_renderer = self.frag_renderer.get_renderer(r.to_node)
                assert isinstance(input_renderer, InputRenderer)
                self.inputs[r.to_node] = input_renderer

    @staticmethod
    def render_loop(render_queue: mp.Queue, inputs: Dict[Node, mp.Queue]):

        q: RenderQueue = render_queue.get()
        if len(q.to_render) == 0:
            # Nothing to do
            render_queue.put(q)
            return

        # Get a block to render
        block = q.to_render.pop(-1)
        render_queue.put(q)

        input_results: Dict[Node, RenderResult] = dict()
        for node in inputs:
            input_results[node] = None

        # Wait for any required inputs to be rendered
        while any(input_results[n] is None for n in input_results):
            time.sleep(0.01)
            for n in input_results:
                input_results[n] = inputs[n].get()
                inputs[n].put(input_results[n])


class InputRenderer(NodeRenderer):

    def __init__(self, node: Node, frag_renderer: FragmentRenderer):
        super().__init__(node, frag_renderer)
        self.inputs: Set[OutputRenderer] = set()

    def on_invalidate(self):

        # Get all the direct inputs to me
        self.inputs = set()
        for r in self.frag_renderer.routes:
            if self.node == r.to_node:
                output_renderer = self.frag_renderer.get_renderer(r.from_node)
                assert isinstance(output_renderer, OutputRenderer)
                self.inputs.add(output_renderer)
