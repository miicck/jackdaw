from Project.LineSerializable import LineSerializable


class MidiNote(LineSerializable):

    def __init__(self, note: str, beat: float):
        """
        A MIDI note data object.
        """
        self.note = note
        self.beat = beat

    def save_to_line(self) -> str:
        """
        Save the data for this midi note
        into a single line of text.
        :return: The line containing saved data.
        """
        return f"{self.note} {self.beat}"

    @classmethod
    def load_from_line(cls, line: str) -> 'MidiNote':
        """
        Creates a MIDI note from a save line.
        :param line: The line containing saved MIDI note data.
        :return: A parsed MidiNote.
        """
        line = line.upper().split()
        note = line[0]
        beat = float(line[1])

        return MidiNote(note, beat)
