import time
import numpy as np
import multiprocessing as mp
from typing import Dict, Tuple, Any, List, Union
from jackdaw.Data import data
from jackdaw.Utils.Singleton import Singleton
from jackdaw.Rendering.ComponentRenderer import ComponentRenderer
from jackdaw.UI.RouterComponents.MasterOutput import MasterOutputData

# Typedefs
NodeKey = Tuple[int, str]
RenderResults = Dict[NodeKey, mp.Queue]


class MultiRenderGraph(Singleton):

    def __init__(self):
        Singleton.__init__(self)
        self._render_results: Dict[NodeKey, Dict[int, np.ndarray]] = dict()
        data.routes.add_on_change_listener(self.recalculate_routes)
        self.recalculate_routes()

    def render_master(self, start: int, samples: int):

        left = None
        right = None

        for route in data.routes:
            from_key = (route.from_component.value, route.from_node.value)
            to_key = (route.to_component.value, route.to_node.value)
            to_comp_data = data.router_components[to_key[0]]
            if isinstance(to_comp_data.component_data, MasterOutputData):
                assert to_key[1] == "To Master"
                if from_key not in self._render_results:
                    raise Exception("Master required input that wasn't rendered!")

                # Accumulate left channel
                if 0 in self._render_results[from_key]:
                    if left is None:
                        left = self._render_results[from_key][0]
                    else:
                        left += self._render_results[from_key][0]

                # Accumulate right channel
                if 1 in self._render_results[from_key]:
                    if right is None:
                        right = self._render_results[from_key][1]
                    else:
                        right += self._render_results[from_key][1]

        if left is None:
            if right is None:
                return np.zeros(1), np.zeros(1)
            return np.zeros(len(right)), right

        if right is None:
            return left, np.zeros(len(left))

        return left, right

    def recalculate_routes(self):

        # Get dictionary of output signals to render
        render_results: RenderResults = dict()
        for route in data.routes:
            key = (route.from_component.value, route.from_node.value)
            render_results[key] = mp.Queue()

        # Initialize render results to None
        for key in render_results:
            render_results[key].put(None)

        # Start render processes
        render_procs = []
        for key in render_results:

            # Get required inputs for this key
            node_inputs: Dict[str, List[NodeKey]] = dict()
            for route in data.routes:
                from_key = (route.from_component.value, route.from_node.value)
                to_key = (route.to_component.value, route.to_node.value)
                if to_key[0] == key[0]:
                    if to_key[1] not in node_inputs:
                        node_inputs[to_key[1]] = []
                    node_inputs[to_key[1]].append(from_key)

            comp_data = data.router_components[key[0]].component_data
            renderer = comp_data.create_component_renderer()
            args = (key, node_inputs, render_results, renderer)
            target = MultiRenderGraph.render_worker
            proc = mp.Process(target=target, args=args)
            proc.start()
            render_procs.append(proc)

        # Join render processes
        for rp in render_procs:
            rp.join()

        # Save the results
        self._render_results.clear()
        for key in render_results:
            self._render_results[key] = render_results[key].get()

    @staticmethod
    def render_worker(key: NodeKey, node_inputs: Dict[str, List[NodeKey]],
                      render_results: RenderResults, renderer: ComponentRenderer):

        # The result type stored in the render results dict
        RenderResult = Dict[int, np.array]
        RenderResult = Union[RenderResult, None]

        # Initialize input results dictionary
        input_results: Dict[NodeKey, RenderResult] = dict()
        for node in node_inputs:
            for input_key in node_inputs[node]:
                input_results[input_key] = None

        # Wait for all required inputs to be rendered
        while any(input_results[input_key] is None for input_key in input_results):
            time.sleep(0.01)
            for input_key in input_results:
                input_results[input_key] = render_results[input_key].get()
                render_results[input_key].put(input_results[input_key])

        # Sum the node input signals to make the node results
        node_results: Dict[str, Dict[int, np.ndarray]] = dict()
        for node in node_inputs:
            node_result = dict()
            for input_key in node_inputs[node]:
                result = input_results[input_key]
                for channel in result:
                    if channel not in node_result:
                        node_result[channel] = result[channel]
                    else:
                        node_result[channel] += result[channel]
            node_results[node] = node_result

        # Perform the render
        render: RenderResult = renderer.render(key[1], 0, node_results)

        # Ensure I haven't somehow been rendered already/save the result
        assert render_results[key].get() is None
        render_results[key].put(render)

        print(f"Rendered component {key[0]} ({renderer.__class__.__name__}), node {key[1]}")
