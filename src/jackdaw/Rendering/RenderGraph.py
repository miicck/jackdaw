from jackdaw.Data import data
from jackdaw.Utils.Singleton import Singleton
from jackdaw.Rendering.ComponentRenderer import ComponentRenderer
from jackdaw.UI.RouterComponents.MasterOutput import MasterOutputRenderer
from typing import Dict, Tuple
import numpy


class RenderGraph(Singleton):

    def __init__(self):
        Singleton.__init__(self)
        self._master_outputs: Dict[int, MasterOutputRenderer] = dict()

        data.router_components.add_on_change_listener(self.recalculate_routes)
        data.routes.add_on_change_listener(self.recalculate_routes)

        self.recalculate_routes()

    def render_master(self, start: int, samples: int) -> Tuple[numpy.ndarray, numpy.ndarray]:

        left = numpy.zeros(samples)
        right = numpy.zeros(samples)

        for master_id in self._master_outputs:
            renderer = self._master_outputs[master_id]

            # Render left channel
            left_r = renderer.render_master(0, start, samples)
            if left_r is not None:
                left += left_r

            # Render right channel
            right_r = renderer.render_master(1, start, samples)
            if right_r is not None:
                right += right_r

        return left, right

    def recalculate_routes(self):

        # Clear the master output renderers
        self._master_outputs.clear()

        # Get the component renderers by id
        renderers: Dict[int, ComponentRenderer] = dict()
        for comp_id in data.router_components:

            # Create the renderer
            comp_data = data.router_components[comp_id].component_data
            renderer = comp_data.create_component_renderer()
            renderers[comp_id] = renderer

            # Record a master output
            if isinstance(renderer, MasterOutputRenderer):
                self._master_outputs[comp_id] = renderer

        # Clear saved input nodes
        for comp_id in renderers:
            renderers[comp_id].clear_input_nodes()

        # Reconstruct input nodes
        for route in data.routes:
            from_id = route.from_component.value
            to_id = route.to_component.value
            from_node = route.from_node.value
            to_node = route.to_node.value

            renderers[to_id].connect_input_node(renderers[from_id], from_node, to_node)
