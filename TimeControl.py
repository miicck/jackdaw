class TimeControl:
    _time = 0.0
    _paused = True
    _bpm = 172.0

    @staticmethod
    def get_time():
        return TimeControl._time

    @staticmethod
    def play():
        TimeControl._paused = False

    @staticmethod
    def pause():
        TimeControl._paused = True

    @staticmethod
    def toggle_play_pause():
        TimeControl._paused = not TimeControl._paused

    @staticmethod
    def stop():
        TimeControl._paused = True
        TimeControl._time = 0.0

    @staticmethod
    def update(self):

        # Advance time if not paused
        if not TimeControl._paused:
            TimeControl._time += 16.0 / 1000.0

        from Playhead import Playhead
        for p in Playhead.playheads:
            p.invoke_position_callback()

        return True

    @staticmethod
    def get_bpm():
        return TimeControl._bpm

    @staticmethod
    def get_time_as_beats():
        return TimeControl.time_to_beats(TimeControl.get_time())

    @staticmethod
    def time_to_beats(time):
        return time * (TimeControl._bpm / 60.0)
