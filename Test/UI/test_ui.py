import time

from UI.Playlist import Playlist
from UI.MidiEditor import MidiEditor
from Project.MidiNote import MidiNote
from Test.Utils.UiTestSession import UiTestSession
import MusicTheory
from Project.PlaylistClipData import PlaylistClipData


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
            pl.data.add(PlaylistClipData(i, i, i % 16))


def test_create_midi_clip():
    with UiTestSession(main_loop_ms=500):
        pl = Playlist.open()
        assert pl is not None

        pl.data.add(PlaylistClipData(1, 0, 0))
        me = MidiEditor.open(1)
        assert me is not None

        beat = 0
        for octave in range(0, MidiEditor.MAX_OCTAVE + 1):
            for note in MusicTheory.NOTES:

                me.clip.add(MidiNote(f"{note}{octave}", beat))

                beat += 0.25
                if beat > 8:
                    beat -= 8

        try:
            me.clip.add(MidiNote("C50", 0))
        except MidiEditor.NoteOutOfRangeException as e:
            assert True
