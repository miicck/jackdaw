from jackdaw.Data.LineSerializable import LineSerializable


class MidiNoteData(LineSerializable):

    def __init__(self, note: str, beat: float):
        """
        Data representing a single MIDI note.
        :param note: The keyboard note e.g "C#5"
        :param beat: The beat location of the note.
        """
        self.note = note
        self.beat = beat

    def copy(self) -> 'MidiNoteData':
        """
        Create a copy of this MIDI note data.
        :return: The MIDI note data copy.
        """
        return MidiNoteData(self.note, self.beat)

    def save_to_line(self) -> str:
        """
        Save the data for this midi note
        into a single line of text.
        :return: The line containing saved data.
        """
        return f"{self.note} {self.beat}"

    @classmethod
    def load_from_line(cls, line: str) -> 'MidiNoteData':
        """
        Creates a MIDI note from a save line.
        :param line: The line containing saved MIDI note data.
        :return: A parsed MidiNote.
        """
        line = line.upper().split()
        note = line[0]
        beat = float(line[1])

        return MidiNoteData(note, beat)
