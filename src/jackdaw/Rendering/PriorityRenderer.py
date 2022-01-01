import time

from jackdaw.Data import data
from jackdaw.Utils.Singleton import Singleton
import multiprocessing as mp
import numpy as np
from jackdaw.Session import session_close_method
from typing import NamedTuple, Set, Dict, List, Tuple, Union
from functools import cmp_to_key
from jackdaw.Data.ProjectData import RouterComponentData
from jackdaw.Rendering.ComponentRenderer import ComponentRenderer
from jackdaw.UI.RouterComponents.MasterOutput import MasterOutputData


# A node is a pair (component id, node name)
class Node(NamedTuple):
    id: int
    node: str


# A route connects two nodes
class Route(NamedTuple):
    from_node: Node
    to_node: Node


# The rendered values of a node
class RenderResult(NamedTuple):
    signal: np.ndarray


# Contains process-safe information
# relating to the rendering queue.
class RenderQueue:

    def __init__(self):
        self.queue = mp.Queue()
        self.queue.put([])

        self.results = mp.Queue()
        self.results.put(dict())

        self.parents = mp.Queue()
        self.parents.put(dict())

        self.node_types = mp.Queue()
        self.node_types.put(dict())


class PriorityRenderer(Singleton):

    def __init__(self):
        Singleton.__init__(self)

        self._routes: Set[Route] = set()
        self._queue = RenderQueue()

        # Create render processes
        self.render_processes: List[mp.Process] = []
        for n in range(mp.cpu_count()):
            args = (self._queue,)
            p = mp.Process(target=PriorityRenderer.render_loop, args=args)
            p.start()
            self.render_processes.append(p)

        data.routes.add_on_change_listener(self.recalculate_routes)
        self.recalculate_routes()

    def render_master(self, start: int, samples: int) -> Tuple[np.ndarray, np.ndarray]:

        master_ids: Set[int] = set()
        for comp_id in data.router_components:
            comp_data = data.router_components[comp_id].component_data
            if isinstance(comp_data, MasterOutputData):
                master_ids.add(comp_id)

        master_nodes: Set[Node] = set()
        for route in self._routes:
            if route.to_node.id in master_ids:
                master_nodes.add(route.to_node)

        all_results = self._queue.results.get()
        self._queue.results.put(all_results)

        channel_res = [None, None]

        for n in master_nodes:
            if n not in all_results:
                continue
            n_res = all_results[n]
            if n_res is None:
                continue
            for i, res in enumerate(channel_res):
                if res is None:
                    channel_res[i] = n_res[i]
                else:
                    channel_res[i] += n_res[i]

        res_len = 1
        for res in channel_res:
            if isinstance(res, np.ndarray):
                res_len = len(res)
                break

        return tuple(c if c is not None else np.zeros(res_len) for c in channel_res)

    def recalculate_routes(self):

        # Get the new set of routes from data
        routes: Set[Route] = {Route(
            Node(r.from_component.value, r.from_node.value),
            Node(r.to_component.value, r.to_node.value)
        ) for r in data.routes}

        # Get the new set of nodes from data
        output_nodes: Set[Node] = {r.from_node for r in routes}
        input_nodes: Set[Node] = {r.to_node for r in routes}
        nodes: Set[Node] = output_nodes.union(input_nodes)
        old_nodes = {r.from_node for r in self._routes}.union({r.to_node for r in self._routes})

        # Work out the parent/child structure
        parents, children = PriorityRenderer.get_parent_dictionary(routes)
        old_parents, old_children = PriorityRenderer.get_parent_dictionary(self._routes)

        # Work out nodes that have been added/removed
        added_nodes = nodes - old_nodes
        removed_nodes = old_nodes - nodes

        # Work out nodes that have been invalidated by this change
        invalidated_nodes: Set[Node] = set()

        # Nodes that are downstream of new nodes are invalidated
        for node in added_nodes:
            invalidated_nodes = invalidated_nodes.union(
                PriorityRenderer.downstream_nodes(node, children))

        # Nodes that were downstream of deleted nodes are invalidated
        for node in removed_nodes:
            invalidated_nodes = invalidated_nodes.union(
                PriorityRenderer.downstream_nodes(node, old_children))

        # Nodes that are currently in the render queue are invalidated
        # (so that previously-queued render jobs are not forgotten about)
        old_queue = self._queue.queue.get()
        self._queue.queue.put(old_queue)
        invalidated_nodes = invalidated_nodes.union(old_queue)

        # Remove any invalid results
        results = self._queue.results.get()
        for n in invalidated_nodes:
            if n in results:
                results.pop(n)
        self._queue.results.put(results)

        # Get component types
        dtypes: Dict[int, str] = dict()
        for comp_id in data.router_components:
            dtypes[comp_id] = data.router_components[comp_id].datatype.value

        # Update node types
        ntypes = self._queue.node_types.get()
        for n in output_nodes:
            ntypes[n] = f"{dtypes[n.id]}.output"
        for n in input_nodes:
            ntypes[n] = f"{dtypes[n.id]}.input"
        self._queue.node_types.put(ntypes)

        # Update parents
        self._queue.parents.get()
        self._queue.parents.put(parents)

        # Update render queue
        self._queue.queue.get()
        queue = [n for n in PriorityRenderer.render_order(parents) if n in invalidated_nodes]
        self._queue.queue.put(queue)

        # Update self
        self._routes = routes

    ################
    # STATIC STUFF #
    ################

    @staticmethod
    def get_parent_dictionary(routes: Set[Route]) -> \
            Tuple[Dict[Node, Set[Node]], Dict[Node, Set[Node]]]:
        # Get the new set of nodes from data
        output_nodes: Set[Node] = {r.from_node for r in routes}
        input_nodes: Set[Node] = {r.to_node for r in routes}
        nodes: Set[Node] = output_nodes.union(input_nodes)

        # Work out the parent structure
        parents: Dict[Node, Set[Node]] = {n: set() for n in nodes}

        # Inter-component parenting
        for r in routes:
            parents[r.to_node].add(r.from_node)

        # Intra-component parenting
        for input_node in input_nodes:
            for output_node in output_nodes:
                if input_node.id == output_node.id:
                    parents[output_node].add(input_node)

        # Get children dictionary
        children: Dict[Node, Set[Node]] = {n: set() for n in nodes}
        for n in nodes:
            for p in parents[n]:
                children[p].add(n)

        return parents, children

    @staticmethod
    def render_order(parents: Dict[Node, Set[Node]]) -> List[Node]:

        # Initially sort by number of parents
        order = list(parents)
        order.sort(key=lambda n: len(parents[n]))

        def dependence_compare(node_left, node_right):
            if node_left in PriorityRenderer.upstream_nodes(node_right, parents):
                return -1
            if node_right in PriorityRenderer.upstream_nodes(node_left, parents):
                return 1
            return 0

        order.sort(key=cmp_to_key(dependence_compare))
        return order

    @staticmethod
    def upstream_nodes(node: Node, parents: Dict[Node, Set[Node]]) -> Set[Node]:

        upstream_nodes = parents[node]
        upstream_nodes.add(node)
        while True:
            length_before = len(upstream_nodes)
            for p in list(upstream_nodes):
                upstream_nodes = upstream_nodes.union(parents[p])
            if len(upstream_nodes) == length_before:
                break

        return upstream_nodes

    @staticmethod
    def downstream_nodes(node: Node, children: Dict[Node, Set[Node]]) -> Set[Node]:

        downstream_nodes = children[node]
        downstream_nodes.add(node)
        while True:
            len_before = len(downstream_nodes)
            for dn in downstream_nodes:
                downstream_nodes = downstream_nodes.union(children[dn])
            if len(downstream_nodes) == len_before:
                break

        return downstream_nodes

    @staticmethod
    @session_close_method
    def close():
        for p in PriorityRenderer.instance().render_processes:
            p.kill()

    @staticmethod
    def render_loop(queue: RenderQueue):

        while True:

            # Get the next node to render
            to_render: List[Node] = queue.queue.get()
            node = None if len(to_render) == 0 else to_render.pop(0)
            queue.queue.put(to_render)

            if node is not None:
                PriorityRenderer.node_render_loop(node, queue)

    @staticmethod
    def node_render_loop(node: Node, queue: RenderQueue):

        while True:

            # Get parents of the node to render
            all_parents = queue.parents.get()
            queue.parents.put(all_parents)

            if node not in all_parents:
                return  # This node no longer exists, so no need to render

            # Query the results queue
            all_results = queue.results.get()
            queue.results.put(all_results)

            # Get results for the parents
            parent_results: Dict[Node, Union[RenderResult, None]] = dict()
            for p in all_parents[node]:
                if p in all_results:
                    parent_results[p] = all_results[p]
                else:
                    parent_results[p] = None

            if any(parent_results[p] is None for p in parent_results):
                # Some parents are un-rendered,
                # wait for a bit, then try again.
                time.sleep(0.01)
                continue

            # Render the node
            PriorityRenderer.render_node(node, parent_results, queue)
            break

    @staticmethod
    def render_node(node: Node,
                    parent_results: Dict[Node, Union[RenderResult, None]],
                    queue: RenderQueue):

        # Ensure parents are properly rendered
        assert all(parent_results[p] is not None for p in parent_results)

        # Get node type
        ntypes: Dict[Node, str] = queue.node_types.get()
        queue.node_types.put(ntypes)
        if node not in ntypes:
            return  # Node has been deleted, no need to render

        dtype, inout = ntypes[node].split(".")
        result: Dict[int, np.ndarray] = None

        if inout == "input":

            # Simply sum contributions to input nodes
            result = dict()
            for p in parent_results:
                pres = parent_results[p]
                for channel in pres:
                    if channel in result:
                        result[channel] += pres[channel]
                    else:
                        result[channel] = pres[channel]

        else:
            # Create the renderer
            renderer: ComponentRenderer = None
            for c in RouterComponentData.__subclasses__():
                if c.__name__ == dtype:
                    renderer = c().create_component_renderer()
            assert renderer is not None

            # Render
            input_results = {p.node: parent_results[p] for p in parent_results}
            result = renderer.render(node.node, 0, input_results)

        assert result is not None

        # Put the result back onto the queue
        res = queue.results.get()
        res[node] = result
        queue.results.put(res)

        print(f"Rendered {node.id}.{node.node} ({dtype}.{inout})")
