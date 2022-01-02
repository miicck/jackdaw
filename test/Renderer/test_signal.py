from jackdaw.Rendering.Signal import Signal
import numpy as np


def test_add():
    a = Signal()
    b = Signal()

    a[0] = np.zeros(3)
    b[0] = np.ones(3)
    b[1] = np.ones(3)

    c = a + b
    assert np.array_equal(c[0], np.ones(3))
    assert np.array_equal(c[1], np.ones(3))
