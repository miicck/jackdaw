from ..Utils.UiTestSession import UiTestSession
from jackdaw.TimeControl import TimeControl
from jackdaw.Gi import add_timeout


def test_time_toggle_play_pause():
    with UiTestSession() as ts:
        def step():
            TimeControl.toggle_play_pause()
            beat_time = TimeControl.get_time_as_beats()
            assert abs(TimeControl.beats_to_time(beat_time) - TimeControl.get_time()) < 10e-5

        add_timeout(step, ts.main_loop_ms // 4, repeats=3)


def test_playhead_time():
    with UiTestSession(main_loop_ms=200) as ts:
        TimeControl.set_playhead_time(4.0)
        assert TimeControl.get_playhead_time() == 4.0
        assert TimeControl.get_time() == 4.0
        TimeControl.pause()

        step = ts.main_loop_ms // 8
        add_timeout(TimeControl.play, step)

        paused_time = 0

        def pause_and_record():
            global paused_time
            TimeControl.pause()
            paused_time = TimeControl.get_time()

        add_timeout(pause_and_record, 2 * step)

        def test_and_play():
            global paused_time
            assert TimeControl.get_time() == paused_time
            TimeControl.play()

        add_timeout(test_and_play, 3 * step)

        def test_stop():
            TimeControl.toggle_play_stop()
            assert TimeControl.get_time() == 4.0

        add_timeout(test_stop, 4 * step)

        def test_unstop():
            assert TimeControl.get_time() == 4.0
            TimeControl.toggle_play_stop()

        add_timeout(test_unstop, 5 * step)
