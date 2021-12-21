class PlaylistClipData:

    def __init__(self, track: int, beat: float):
        self.track = track
        self.beat = beat

    def save_to_line(self) -> str:
        return f"{self.track} {self.beat}"

    @staticmethod
    def load_from_line(self, line: str) -> 'PlaylistClipData':
        line = line.split()
        track = int(line[0])
        beat = float(line[1])

        return PlaylistClipData(track, beat)
