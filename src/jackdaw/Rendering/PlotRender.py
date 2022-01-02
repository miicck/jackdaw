import matplotlib.pyplot as plt
from jackdaw.Rendering.PriorityRenderer import PriorityRenderer


def plot_left_right(left, right):
    plt.subplot(211)
    plt.plot(left)
    plt.subplot(212)
    plt.plot(right)
    plt.show()


def plot_priority_render(start: int, samples: int):
    plot_left_right(*PriorityRenderer.instance().render_master(start, samples))
