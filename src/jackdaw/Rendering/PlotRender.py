import matplotlib.pyplot as plt
from jackdaw.Rendering.RenderGraph import RenderGraph


def plot_render(start: int, samples: int):
    rg: RenderGraph = RenderGraph.instance()
    left, right = rg.render_master(start, samples)

    plt.subplot(211)
    plt.plot(left)

    plt.subplot(212)
    plt.plot(right)

    plt.show()
