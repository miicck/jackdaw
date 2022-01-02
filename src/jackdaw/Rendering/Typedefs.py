from typing import NamedTuple


# A node is a pair (component id, node name)
class Node(NamedTuple):
    id: int
    node: str


# A route connects two nodes
class Route(NamedTuple):
    from_node: Node
    to_node: Node
