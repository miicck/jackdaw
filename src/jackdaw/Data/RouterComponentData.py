from jackdaw.Data.LineSerializable import LineSerializable
from typing import Tuple


class RouterComponentData(LineSerializable):

    def __init__(self, component_type: str, position: Tuple[float, float]):
        self.component_type = component_type
        self.position = position

    def save_to_line(self) -> str:
        return f"{self.component_type} {self.position[0]} {self.position[1]}"

    @classmethod
    def load_from_line(cls, line: str) -> 'RouterComponentData':
        line = line.split()
        component_type = line[0]
        position = (float(line[1]), float(line[2]))

        return RouterComponentData(component_type, position)
