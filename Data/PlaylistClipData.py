from Data.LineSerializable import LineSerializable


class PlaylistClipData(LineSerializable):

    def __init__(self, clip_number: int, track: int, beat: float):
        """
        Data representing a playlist clip entry.
        :param clip_number: The unique clip number.
        :param track: The track that this clip is on.
        :param beat: The beat that this track is at.
        """
        self.clip_number = clip_number
        self.track = track
        self.beat = beat

    def save_to_line(self) -> str:
        """
        Save the data for this clip to a single-line string.
        :return: The single-line string serialization of this clip.
        """
        return f"{self.clip_number} {self.track} {self.beat}"

    @classmethod
    def load_from_line(cls, line: str) -> 'PlaylistClipData':
        """
        Deserialize playlist clip data from the given line.
        :param line: A single-line serialization of a playlist clip.
        :return: The deserialized playlist clip data object.
        """
        line = line.split()

        clip_number = int(line[0])
        track = int(line[1])
        beat = float(line[2])

        return PlaylistClipData(clip_number, track, beat)
