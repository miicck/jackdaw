import jackdaw.Data.ProjectData
from ..Utils.UiTestSession import UiTestSession
from jackdaw.UI.MidiEditor import MidiEditor
from jackdaw.UI.Router import Router
from jackdaw.Data import data
from jackdaw.Data.ProjectData import MidiNoteData
from jackdaw.Data.ProjectData import PlaylistClipData
from jackdaw import MusicTheory


def test_save_playlist():
    saved = set()

    with UiTestSession(save_project=True):
        for i in range(25):
            to_check = (i, i, i % 16)

            clip = PlaylistClipData()
            clip.clip.value = to_check[0]
            clip.track.value = to_check[1]
            clip.beat.value = to_check[2]
            data.playlist_clips.add(clip)

            saved.add(to_check)

    with UiTestSession():
        for c in data.playlist_clips:
            to_check = (c.clip.value, c.track.value, c.beat.value)
            assert to_check in saved
            saved.remove(to_check)

    assert len(saved) == 0


def test_save_playlist_with_clip_destroy():
    saved = set()

    with UiTestSession(save_project=True):
        for i in range(25):
            to_check = (i, i, i % 16)

            clip_data = PlaylistClipData()
            clip_data.clip.value = to_check[0]
            clip_data.track.value = to_check[1]
            clip_data.beat.value = to_check[2]

            data.playlist_clips.add(clip_data)

            if i % 3 == 0:
                data.playlist_clips.remove(clip_data)
            else:
                saved.add(to_check)

    with UiTestSession():
        for c in data.playlist_clips:
            to_check = (c.clip.value, c.track.value, c.beat.value)
            assert to_check in saved
            saved.remove(to_check)

    assert len(saved) == 0


def test_save_midi_clip():
    saved = set()

    with UiTestSession(save_project=True):

        beat = 0
        for octave in range(MidiEditor.MAX_OCTAVE + 1):
            for note in MusicTheory.NOTES:
                to_check = (f"{note}{octave}", beat % 16)

                note = MidiNoteData()
                note.note.value = to_check[0]
                note.beat.value = to_check[1]

                data.midi_clips[1].notes.add(note)

                saved.add(to_check)
                beat += 1

    with UiTestSession():
        for note in data.midi_clips[1].notes:
            to_check = (note.note.value, note.beat.value)
            assert to_check in saved
            saved.remove(to_check)

    assert len(saved) == 0


def test_save_midi_clip_with_delete():
    saved = set()

    with UiTestSession(save_project=True):

        beat = 0
        for octave in range(MidiEditor.MAX_OCTAVE + 1):
            for note in MusicTheory.NOTES:
                to_check = (f"{note}{octave}", beat % 16)

                note = MidiNoteData()
                note.note.value = to_check[0]
                note.beat.value = to_check[1]
                data.midi_clips[1].notes.add(note)

                if beat % 3 == 0:
                    data.midi_clips[1].notes.remove(note)
                else:
                    saved.add(to_check)

                beat += 1

    with UiTestSession():
        for note in data.midi_clips[1].notes:
            to_check = (note.note.value, note.beat.value)
            assert to_check in saved
            saved.remove(to_check)

    assert len(saved) == 0


def test_save_router():
    with UiTestSession(save_project=True):
        r = Router.open()
        r.add_track_signal(100, 100)
        assert len(data.router_components) == 1

    with UiTestSession():
        assert len(data.router_components) == 1
