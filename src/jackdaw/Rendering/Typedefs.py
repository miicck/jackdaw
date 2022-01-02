from typing import NamedTuple, Union, Dict
import numpy as np


# A node is a pair (component id, node name)
class Node(NamedTuple):
    id: int
    node: str


# A route connects two nodes
class Route(NamedTuple):
    from_node: Node
    to_node: Node


# A channel is an array of data in a channel (or none => no data)
ChannelData = Union[np.ndarray, None]
