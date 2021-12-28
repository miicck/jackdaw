import matplotlib.pyplot as plt
from jackdaw.Rendering.RenderGraph import RenderGraph
from jackdaw.Rendering.MultiRenderGraph import MultiRenderGraph


def plot_render(start: int, samples: int):
    rg: RenderGraph = RenderGraph.instance()
    left, right = rg.render_master(start, samples)

    plt.subplot(211)
    plt.plot(left)

    plt.subplot(212)
    plt.plot(right)

    plt.show()


def plot_multi_render(start: int, samples: int):
    mrg = MultiRenderGraph.instance()
    left, right = mrg.render_master(start, samples)

    plt.subplot(211)
    plt.plot(left)

    plt.subplot(212)
    plt.plot(right)

    plt.show()
