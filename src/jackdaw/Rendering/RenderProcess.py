import numpy as np
from jackdaw.Rendering.RenderGraph import RenderGraph
import multiprocessing
import pyaudio
import numpy
from jackdaw.Utils.Singleton import Singleton


class RenderProcess(Singleton):

    def __init__(self):
        Singleton.__init__(self)
        self.render_graph = RenderGraph.instance()
        self.play_event = multiprocessing.Event()
        self.kill_event = multiprocessing.Event()
        self.process = multiprocessing.Process(target=self.render_loop)
        self.process.start()

    def render_loop(self):

        session = pyaudio.PyAudio()
        stream = session.open(format=pyaudio.paFloat32, rate=44100, channels=2, output=True)

        i = 0
        chunk_size = 256
        while True:

            if self.kill_event.is_set():
                break

            if not self.play_event.is_set():
                i = 0
                continue

            left, right = self.render_graph.render_master(i, chunk_size)
            interleaved = np.empty(chunk_size * 2, dtype=numpy.float32)
            interleaved[0::2] = left
            interleaved[1::2] = right
            stream.write(interleaved.tobytes(), num_frames=chunk_size)
            i += chunk_size

        stream.stop_stream()
        stream.close()
        session.terminate()

    def play(self):
        self.play_event.set()

    def stop(self):
        self.play_event.clear()

    def kill(self):
        self.kill_event.set()
