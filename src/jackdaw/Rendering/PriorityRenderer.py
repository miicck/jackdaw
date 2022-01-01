from jackdaw.Data import data
from jackdaw.Utils.Singleton import Singleton
import multiprocessing as mp
import numpy as np
from jackdaw.Session import session_close_method
from typing import NamedTuple, Set, Dict, List, Tuple
from functools import cmp_to_key


# A node is a pair (component id, node name)
class Node(NamedTuple):
    id: int
    node: str


# A route connects two nodes
class Route(NamedTuple):
    from_node: Node
    to_node: Node


class PriorityRenderer(Singleton):

    def __init__(self):
        Singleton.__init__(self)

        self._routes: Set[Route] = set()

        self.queue = mp.Queue()
        self.queue.put([])

        self.results = mp.Queue()
        self.results.put(dict())

        self.graph = mp.Queue()
        self.graph.put(dict())

        self.render_processes = []
        for n in range(mp.cpu_count()):
            args = (self.queue, self.results, self.graph,)
            p = mp.Process(target=PriorityRenderer.render_loop, args=args)
            p.start()
            self.render_processes.append(p)

        data.routes.add_on_change_listener(self.recalculate_routes)

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

        # Work out the parent/child structure
        parents, children = self.get_parent_dictionary(routes)
        old_parents, old_children = self.get_parent_dictionary(self._routes)

        # Work out nodes that have been added/removed
        added_nodes = nodes - self.nodes
        removed_nodes = self.nodes - nodes

        # Work out nodes that have been invalidated by this change
        invalidated_nodes: Set[Node] = set()

        # Nodes that are downstream of new nodes are invalidated
        for node in added_nodes:
            invalidated_nodes = invalidated_nodes.union(
                self.downstream_nodes(node, children))

        # Nodes that were downstream of deleted nodes are invalidated
        for node in removed_nodes:
            invalidated_nodes = invalidated_nodes.union(
                self.downstream_nodes(node, old_children))

        # Get the render order queue
        order = [n for n in self.get_render_order(parents) if n in invalidated_nodes]
        print(f"Rendering {order}")

        # Update self
        self._routes = routes

    def get_parent_dictionary(self, routes: Set[Route]) -> \
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

    def get_render_order(self, parents: Dict[Node, Set[Node]]) -> List[Node]:

        # Initially sort by number of parents
        order = list(parents)
        order.sort(key=lambda n: len(parents[n]))

        def dependence_compare(node_left, node_right):
            if node_left in self.upstream_nodes(node_right, parents):
                return -1
            if node_right in self.upstream_nodes(node_left, parents):
                return 1
            return 0

        order.sort(key=cmp_to_key(dependence_compare))
        return order

    def upstream_nodes(self, node: Node, parents: Dict[Node, Set[Node]]) -> Set[Node]:

        upstream_nodes = parents[node]
        upstream_nodes.add(node)
        while True:
            length_before = len(upstream_nodes)
            for p in list(upstream_nodes):
                upstream_nodes = upstream_nodes.union(parents[p])
            if len(upstream_nodes) == length_before:
                break

        return upstream_nodes

    def downstream_nodes(self, node: Node, children: Dict[Node, Set[Node]]) -> Set[Node]:

        downstream_nodes = children[node]
        downstream_nodes.add(node)
        while True:
            len_before = len(downstream_nodes)
            for dn in downstream_nodes:
                downstream_nodes = downstream_nodes.union(children[dn])
            if len(downstream_nodes) == len_before:
                break

        return downstream_nodes

    ##############
    # PROPERTIES #
    ##############

    @property
    def routes(self) -> Set[Route]:
        return self._routes

    @property
    def input_nodes(self) -> Set[Node]:
        return {r.to_node for r in self.routes}

    @property
    def output_nodes(self) -> Set[Node]:
        return {r.from_node for r in self.routes}

    @property
    def nodes(self) -> Set[Node]:
        return self.input_nodes.union(self.output_nodes)

    ################
    # STATIC STUFF #
    ################

    @staticmethod
    @session_close_method
    def close():
        for p in PriorityRenderer.instance().render_processes:
            p.kill()

    @staticmethod
    def render_loop(queue: mp.Queue, results: mp.Queue, graph: mp.Queue):
        pass
