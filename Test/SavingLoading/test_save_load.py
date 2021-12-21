from Test.Utils.UiTestSession import UiTestSession
from UI.Playlist import Playlist
from UI.MidiEditor import MidiEditor
import MusicTheory


def test_save_playlist():
    saved = set()

    with UiTestSession(save_project=True):
        pl = Playlist.open()
        for i in range(25):
            data = (i, i, i % 16)
            pl.create_clip(*data)
            saved.add(data)

    with UiTestSession():
        pl = Playlist.open()
        for c in pl.clips:
            data = (c.clip_number, c.track, c.beat)
            assert data in saved
            saved.remove(data)

    assert len(saved) == 0


def test_save_playlist_with_clip_destroy():
    saved = set()

    with UiTestSession(save_project=True):
        pl = Playlist.open()
        for i in range(25):
            data = (i, i, i % 16)
            clip = pl.create_clip(*data)

            if i % 3 == 0:
                clip.destroy()
            else:
                saved.add(data)

    with UiTestSession():
        pl = Playlist.open()
        for c in pl.clips:
            data = (c.clip_number, c.track, c.beat)
            assert data in saved
            saved.remove(data)

    assert len(saved) == 0


def test_save_midi_clip():
    saved = set()

    with UiTestSession(save_project=True):
        me = MidiEditor.open(1)
        beat = 0
        for octave in range(MidiEditor.MAX_OCTAVE + 1):
            for note in MusicTheory.NOTES:
                name = f"{note}{octave}"
                data = (name, beat % 16)
                me.add_note(*data)
                saved.add(data)
                beat += 1

    with UiTestSession():
        me = MidiEditor.open(1)
        for note in me.notes:
            data = (note.note, note.beat)
            assert data in saved
            saved.remove(data)

    assert len(saved) == 0


def test_save_midi_with_note_destroy():
    saved = set()

    with UiTestSession(save_project=True):
        me = MidiEditor.open(1)
        beat = 0
        for octave in range(MidiEditor.MAX_OCTAVE + 1):
            for note in MusicTheory.NOTES:
                name = f"{note}{octave}"
                data = (name, beat % 16)
                beat += 1

                added = me.add_note(*data)
                if octave % 3 == 0:
                    added.destroy()
                else:
                    saved.add(data)

    with UiTestSession():
        me = MidiEditor.open(1)
        for note in me.notes:
            data = (note.note, note.beat)
            assert data in saved
            saved.remove(data)

    assert len(saved) == 0
