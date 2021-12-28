from jackdaw.Data import data
from jackdaw.Utils.Singleton import Singleton
import multiprocessing as mp
from typing import Dict, Tuple, Any
import numpy

# Typedef
RenderResults = Dict[Tuple[int, str], mp.Queue]


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
            from_id = route.from_component.value
            from_node = route.from_node.value
            render_results[(from_id, from_node)] = mp.Queue()

        # Initialize render results to None
        for key in render_results:
            render_results[key].put(None)

        # Start render processes
        render_procs = []
        for key in render_results:
            args = (key, render_results,)
            target = MultiRenderGraph.render_worker
            proc = mp.Process(target=target, args=args)
            proc.start()
            render_procs.append(proc)

        # Join render processes
        for rp in render_procs:
            rp.join()

    @staticmethod
    def render_worker(key: Tuple[int, str], render_results: RenderResults):
        print(key)
