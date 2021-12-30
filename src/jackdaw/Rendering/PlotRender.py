import matplotlib.pyplot as plt
from jackdaw.Rendering.RenderGraph import RenderGraph
from jackdaw.Rendering.MultiRenderGraph import MultiRenderGraph
from jackdaw.Rendering.FragmentRenderer import FragmentRenderer


def plot_left_right(left, right):
    plt.subplot(211)
    plt.plot(left)
    plt.subplot(212)
    plt.plot(right)
    plt.show()


def plot_render(start: int, samples: int):
    plot_left_right(*RenderGraph.instance().render_master(start, samples))


def plot_multi_render(start: int, samples: int):
    plot_left_right(*MultiRenderGraph.instance().render_master(start, samples))


def plot_fragment_render(start: int, samples: int):
    plot_left_right(*FragmentRenderer.instance().render_master(start, samples))
