class TimeControl:
    _time = 0.0
    _playhead_time = 0.0
    _paused = True
    _bpm = 172.0

    @staticmethod
    def get_time():
        return TimeControl._time

    @staticmethod
    def get_bpm():
        return TimeControl._bpm

    @staticmethod
    def get_playhead_time():
        return TimeControl._playhead_time

    @staticmethod
    def set_playhead_time(time):
        TimeControl._playhead_time = time
        TimeControl._time = time

    @staticmethod
    def get_time_as_beats():
        return TimeControl.time_to_beats(TimeControl.get_time())

    @staticmethod
    def time_to_beats(time):
        return time * TimeControl._bpm / 60.0

    @staticmethod
    def beats_to_time(beats):
        return 60.0 * beats / TimeControl._bpm

    @staticmethod
    def play():
        TimeControl._paused = False

    @staticmethod
    def pause():
        TimeControl._paused = True

    @staticmethod
    def stop():
        TimeControl._paused = True
        TimeControl._time = TimeControl._playhead_time

    @staticmethod
    def toggle_play_pause():
        TimeControl._paused = not TimeControl._paused

    @staticmethod
    def toggle_play_stop():
        if TimeControl._paused:
            TimeControl.play()
        else:
            TimeControl.stop()

    @staticmethod
    def update():

        # Advance time if not paused
        if not TimeControl._paused:
            TimeControl._time += 16.0 / 1000.0

        from jackdaw.UI.Playhead import Playhead
        for p in Playhead.playheads:
            p.invoke_position_callback()

        return True
