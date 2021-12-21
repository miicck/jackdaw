import time

from UI.Playlist import Playlist
from UI.MidiEditor import MidiEditor
from Project.MidiNote import MidiNote
from Test.Utils.UiTestSession import UiTestSession
import MusicTheory


def test_open_playlist():
    with UiTestSession():
        assert Playlist.open() is not None


def test_open_midi_editor():
    with UiTestSession():
        assert MidiEditor.open(1) is not None


def test_open_close_midi_editor():
    with UiTestSession():
        for i in range(10):
            assert MidiEditor.open(i) is not None
            MidiEditor.close(i)


def test_open_many_midi_editors():
    with UiTestSession(main_loop_ms=500):
        for i in range(10):
            assert MidiEditor.open(i) is not None


def test_create_playlist_clips():
    with UiTestSession():
        pl = Playlist()
        for i in range(100):
            pl.create_clip(i, i, i)


def test_create_midi_clip():
    with UiTestSession(main_loop_ms=500):
        pl = Playlist.open()
        assert pl is not None

        clip = pl.create_clip(0, 0, 1)
        assert clip is not None

        me = clip.open_midi_editor()
        assert me is not None

        beat = 0
        for octave in range(0, MidiEditor.MAX_OCTAVE + 1):
            for note in MusicTheory.NOTES:

                me.clip.add_note(MidiNote(f"{note}{octave}", beat))

                beat += 0.25
                if beat > 8:
                    beat -= 8

        try:
            me.clip.add_note(MidiNote("C50", 0))
        except MidiEditor.NoteOutOfRangeException as e:
            assert True
