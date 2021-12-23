import json
from DataObjects import *


class MidiNoteData(DataObject):

    def __init__(self):
        self.note = RawDataObject("C3")
        self.beat = RawDataObject(0.0)


class MidiClipData(DataObject):

    def __init__(self):
        self.notes = DataObjectDict(MidiNoteData)


class PlaylistClipData(DataObject):

    def __init__(self):
        self.clip = RawDataObject(0)
        self.track = RawDataObject(0)
        self.beat = RawDataObject(0.0)
        self.type = RawDataObject("MIDI")


class ProjectData(DataObject):

    def __init__(self):
        super().__init__()
        self.midi_clips = DataObjectDict(MidiClipData)
        self.playlist_clips = DataObjectDict(PlaylistClipData)


########
# TEST #
########

data = ProjectData()
for i in range(2):
    for j in range(3):
        assert data.midi_clips[i].notes[j] is not None

    data.midi_clips[0].notes[0].note.value = "C4"

for i in range(2):
    assert data.playlist_clips[i] is not None


def pretty_json(tree):
    indent = 2
    s = json.dumps(tree, indent=indent)
    for r in {"{", "}", ",", "\"", ":"}:
        s = s.replace(r, "")

    lines = []
    for line in s.split("\n"):
        if len(line.strip()) > 0:
            lines.append(line[indent:])

    return "\n".join(lines)


print(pretty_json(data.serialize()))
