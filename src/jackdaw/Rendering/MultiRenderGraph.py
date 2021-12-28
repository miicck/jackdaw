from jackdaw.Data import data
from jackdaw.Utils.Singleton import Singleton
import multiprocessing as mp
from typing import Dict, Tuple, Any, List
import numpy

# Typedefs
NodeKey = Tuple[int, str]
RenderResults = Dict[NodeKey, mp.Queue]


class MultiRenderGraph(Singleton):

    def __init__(self):
        Singleton.__init__(self)

        data.router_components.add_on_change_listener(self.recalculate_routes)
        data.routes.add_on_change_listener(self.recalculate_routes)

        self.recalculate_routes()

    def render_master(self, start: int, samples: int):
        return numpy.zeros(samples), numpy.zeros(samples)

    def recalculate_routes(self):

        # Get dictionary of output signals to render
        render_results: RenderResults = dict()
        for route in data.routes:
            key = (route.from_component.value, route.from_node.value)
            render_results[key] = mp.Queue()

        # Get dictionary of input signal dependence
        needed_inputs: Dict[int, List[NodeKey]] = dict()
        for route in data.routes:
            from_key = (route.from_component.value, route.from_node.value)
            to_id = route.to_component.value
            if to_id not in needed_inputs:
                needed_inputs[to_id] = []
            needed_inputs[to_id].append(from_key)

        # Initialize render results to None
        for key in render_results:
            render_results[key].put(None)

        # Start render processes
        render_procs = []
        for key in render_results:
            inputs = []
            if key[0] in needed_inputs:
                inputs = needed_inputs[key[0]]
            args = (key, inputs, render_results,)
            target = MultiRenderGraph.render_worker
            proc = mp.Process(target=target, args=args)
            proc.start()
            render_procs.append(proc)

        # Join render processes
        for rp in render_procs:
            rp.join()

    @staticmethod
    def render_worker(key: NodeKey, inputs: List[NodeKey],
                      render_results: RenderResults):
        print(key, inputs)
