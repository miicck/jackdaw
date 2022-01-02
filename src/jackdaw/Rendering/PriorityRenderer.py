import time
import numpy as np
import multiprocessing as mp
from functools import cmp_to_key
from typing import Set, List, Tuple, NamedTuple, Dict, Union

from jackdaw.Data import data
from jackdaw.Utils.Singleton import Singleton
from jackdaw.Data.ProjectData import RouterComponentData
from jackdaw.Rendering.ComponentRenderer import ComponentRenderer
from jackdaw.UI.RouterComponents.MasterOutput import MasterOutputData
from jackdaw.Rendering.Signal import Signal


# A node is a pair (component id, node name)
class Node(NamedTuple):
    id: int
    node: str


# A route connects two nodes
class Route(NamedTuple):
    from_node: Node
    to_node: Node


# Contains process-safe information
# relating to the rendering queue.
class RenderQueue:

    def __init__(self):
        self.kill_switch = mp.Queue()
        self.kill_switch.put(False)

        self.queue = mp.Queue()
        self.queue.put([])

        self.results = mp.Queue()
        self.results.put(dict())

        self._parents = mp.Queue()
        self._parents.put(dict())

        self.node_types = mp.Queue()
        self.node_types.put(dict())

    @property
    def parents(self) -> Dict[Node, Set[Node]]:
        par = self._parents.get()
        self._parents.put(par)

        for n in par:
            assert n not in par[n]

        return par

    @parents.setter
    def parents(self, par: Dict[Node, Set[Node]]):
        self._parents.get()
        self._parents.put(par)

        for n in par:
            assert n not in par[n]

    @property
    def killed(self):
        killed = self.kill_switch.get()
        self.kill_switch.put(killed)
        return killed

    @killed.setter
    def killed(self, val: bool):
        self.kill_switch.get()
        self.kill_switch.put(val)


class PriorityRenderer(Singleton):

    def __init__(self):
        Singleton.__init__(self)

        # Initialize the set of routes amd the render queue
        self._routes: Set[Route] = set()
        self._queue = RenderQueue()

        # Create render processes
        self._render_processes: List[mp.Process] = []
        for n in range(mp.cpu_count()):
            p = mp.Process(target=PriorityRenderer.render_loop,
                           args=(self._queue,),
                           name=f"Renderer {len(self._render_processes)}")
            p.start()
            self._render_processes.append(p)

        data.routes.add_on_change_listener(self.recalculate_routes)
        self.recalculate_routes()

    def render_master(self, start: int, samples: int) -> Tuple[np.ndarray, np.ndarray]:

        # Wait for render queue
        queue = [None]
        while len(queue) > 0:
            queue = self._queue.queue.get()
            self._queue.queue.put(queue)
            time.sleep(0.01)

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

        result = Signal.sum(all_results[n] for n in master_nodes if n in all_results)
        return result[0], result[1]

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
        added_routes = routes - self._routes
        removed_routes = self._routes - routes

        # Work out nodes that have been invalidated by this change
        invalidated_nodes: Set[Node] = set()

        # Nodes that are downstream of new routes are invalidated
        for route in added_routes:
            invalidated_nodes = invalidated_nodes.union(
                PriorityRenderer.downstream_nodes(route.to_node, children))

        # Nodes that were downstream of deleted routes are invalidated
        for route in removed_routes:
            invalidated_nodes = invalidated_nodes.union(
                PriorityRenderer.downstream_nodes(route.to_node, old_children))

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
        self._queue.parents = parents

        # Update render queue
        self._queue.queue.get()
        queue = [n for n in PriorityRenderer.render_order(parents) if n in invalidated_nodes]
        self._queue.queue.put(queue)

        # Update self
        self._routes = routes

    def on_clear_singleton_instance(self):
        self._queue.killed = True
        for p in self._render_processes:
            p.join()

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

    #####################
    # RENDERING PROCESS #
    #####################

    @staticmethod
    def render_loop(queue: RenderQueue):

        while not queue.killed:

            time.sleep(0.01)

            # Get the next node to render
            to_render: List[Node] = queue.queue.get()
            node = None if len(to_render) == 0 else to_render.pop(0)
            queue.queue.put(to_render)

            if node is not None:
                PriorityRenderer.node_render_loop(node, queue)

        print("Render process finished")

    @staticmethod
    def node_render_loop(node: Node, queue: RenderQueue):

        print(f"Started rendering {node.id}.{node.node}")

        while not queue.killed:

            # Get parents of the node to render
            all_parents = queue.parents

            if node not in all_parents:
                return  # This node no longer exists, so no need to render

            # Query the results queue
            all_results = queue.results.get()
            queue.results.put(all_results)

            # Get results for the parents
            parent_results: Dict[Node, Union[Signal, None]] = dict()
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
                    parent_results: Dict[Node, Signal],
                    queue: RenderQueue):

        # Ensure parents are properly rendered
        assert all(parent_results[p] is not None for p in parent_results)

        # Get node type
        ntypes: Dict[Node, str] = queue.node_types.get()
        queue.node_types.put(ntypes)
        if node not in ntypes:
            return  # Node has been deleted, no need to render

        dtype, inout = ntypes[node].split(".")
        result: Union[Signal, None] = None

        if inout == "input":

            # Simply sum contributions to input nodes
            result = Signal()
            for p in parent_results:
                pres = parent_results[p]
                for channel in pres:
                    if channel in result:
                        result[channel] += pres[channel]
                    else:
                        result[channel] = pres[channel]

        else:
            # Create the renderer
            renderer: Union[ComponentRenderer, None] = None
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
