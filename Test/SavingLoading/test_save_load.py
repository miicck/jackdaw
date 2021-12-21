from Test.Utils.UiTestSession import UiTestSession
from UI.Playlist import Playlist
from UI.MidiEditor import MidiEditor
from Project.MidiNote import MidiNote
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
                data = (f"{note}{octave}", beat % 16)
                me.clip.add_note(MidiNote(*data))
                saved.add(data)
                beat += 1

    with UiTestSession():
        me = MidiEditor.open(1)
        for note in me.clip.notes:
            data = (note.note, note.beat)
            assert data in saved
            saved.remove(data)

    assert len(saved) == 0


def test_save_midi_clip_with_delete():
    saved = set()

    with UiTestSession(save_project=True):

        assert len(MidiEditor.open_editors) == 0

        me = MidiEditor.open(1)
        assert len(me.clip.notes) == 0

        beat = 0
        for octave in range(MidiEditor.MAX_OCTAVE + 1):
            for note in MusicTheory.NOTES:
                data = (f"{note}{octave}", beat % 16)

                note = MidiNote(*data)
                me.clip.add_note(note)

                if beat % 3 == 0:
                    me.clip.remote_note(note)
                else:
                    saved.add(data)

                beat += 1

    with UiTestSession():
        me = MidiEditor.open(1)
        for note in me.clip.notes:
            data = (note.note, note.beat)
            assert data in saved
            saved.remove(data)

    assert len(saved) == 0
