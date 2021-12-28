import multiprocessing
from typing import List, Tuple, Dict
import time


def render(comp_id: int, parents: List[int], render_results: Dict[int, multiprocessing.Queue]):
    # Wait for all parents to be rendered
    parent_results = [None] * len(parents)
    while not all(r is not None for r in parent_results):
        time.sleep(0.01)
        for i, p in enumerate(parents):
            parent_results[i] = render_results[p].get()
            render_results[p].put(parent_results[i])

    print(f"Parents of {comp_id} complete")

    # Check that I have not yet been rendered
    assert render_results[comp_id].get() is None

    if len(parents) == 0:
        # Generate my result
        render_results[comp_id].put(comp_id)
    else:
        # Combine parent results
        render_results[comp_id].put(sum(r for r in parent_results))


def render_all(graph: List[Tuple[int, int]]):
    # Get all the component ids in the graph
    ids = set()
    for i, j in graph:
        ids.add(i)
        ids.add(j)

    # Set up the render queues for the graph
    render_results = {i: multiprocessing.Queue() for i in ids}
    for i in ids:
        render_results[i].put(None)

    # Start a render job for each component
    procs = []
    for comp_id in ids:
        parents = [i for i, j in graph if j == comp_id]
        args = (comp_id, parents, render_results,)
        p = multiprocessing.Process(target=render, args=args)
        p.start()
        procs.append(p)

    # Join all processes
    for p in procs:
        p.join()

    # Print results
    render_results = {i: render_results[i].get() for i in ids}
    print(render_results)


render_all([
    (3, 5),
    (4, 5),
    (0, 3),
    (1, 3),
    (2, 4)
])
