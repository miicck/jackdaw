from Project.LineSerializable import LineSerializable


class PlaylistClipData(LineSerializable):

    def __init__(self, clip_number: int, track: int, beat: float):
        self.clip_number = clip_number
        self.track = track
        self.beat = beat

    def save_to_line(self) -> str:
        return f"{self.clip_number} {self.track} {self.beat}"

    @classmethod
    def load_from_line(cls, line: str) -> 'PlaylistClipData':
        line = line.split()

        clip_number = int(line[0])
        track = int(line[1])
        beat = float(line[2])

        return PlaylistClipData(clip_number, track, beat)
