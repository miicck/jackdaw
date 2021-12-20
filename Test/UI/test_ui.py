import time

from UI.Playlist import Playlist
from UI.MidiEditor import MidiEditor
from Test.Utils.UiTestSession import UiTestSession
import MusicTheory


def test_open_playlist():
    with UiTestSession():
        assert Playlist.open() is not None


def test_open_midi_editor():
    with UiTestSession():
        assert MidiEditor.open(1) is not None


def test_create_midi_clip():
    with UiTestSession(main_loop_ms=500):
        pl = Playlist.open()
        assert pl is not None

        clip = pl.create_clip(0, 0, 1)
        assert clip is not None

        me = clip.open_midi_editor()
        assert me is not None

        beat = 0
        for octave in range(-4, 20):
            for note in MusicTheory.NOTES:
                name = f"{note}{octave}"
                beat += 0.25

                if beat > 8:
                    beat -= 8

                try:
                    me.add_note(name, beat)
                except MidiEditor.NoteOutOfRangeException:
                    assert octave < 0 or octave > MidiEditor.MAX_OCTAVE
