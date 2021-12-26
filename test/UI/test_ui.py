from ..Utils.UiTestSession import UiTestSession
from jackdaw.UI.Playlist import Playlist
from jackdaw.UI.MidiEditor import MidiEditor
from jackdaw.Data import data
from jackdaw.Data.ProjectData import MidiNoteData, MidiClipData
from jackdaw.Data.ProjectData import PlaylistClipData
from jackdaw import MusicTheory
from jackdaw.Gi import add_timeout
from jackdaw.UI.Router import Router
from jackdaw.UI.ControlPanel import ControlPanel


def test_control_panel():
    with UiTestSession():
        ControlPanel.instance()


def test_open_playlist():
    with UiTestSession():
        assert Playlist.instance() is not None


def test_open_midi_editor():
    with UiTestSession():
        assert MidiEditor.open(1) is not None


def test_open_close_midi_editor():
    with UiTestSession():
        for i in range(10):
            assert MidiEditor.open(i) is not None
            MidiEditor.close(i)


def test_open_many_midi_editors():
    with UiTestSession() as ts:
        def add_editor():
            number = len(MidiEditor.open_editors) + 1
            assert MidiEditor.open(number) is not None

        add_timeout(add_editor, ts.main_loop_ms // 100, repeats=10)


def test_create_playlist_clips():
    with UiTestSession():
        for i in range(100):
            clip = PlaylistClipData()
            clip.beat.value = i % 16
            clip.track.value = i
            data.playlist_clips.add(clip)

        Playlist.instance()


def test_playlist_paste_clip():
    with UiTestSession():
        pl = Playlist.instance()
        pl.paste_clip(100, 100)
        assert len(list(pl.ui_clips)) == 1
        assert len(data.playlist_clips) == 1


def test_create_midi_clip():
    with UiTestSession():

        # Create the midi clip
        data.midi_clips[1] = MidiClipData()

        # Add notes to midi clip
        beat = 0
        for octave in range(0, MidiEditor.MAX_OCTAVE + 1):
            for note in MusicTheory.NOTES:

                note_data = MidiNoteData()
                note_data.note.value = f"{note}{octave}"
                note_data.beat.value = beat
                data.midi_clips[1].notes.add(note_data)

                beat += 0.25
                if beat > 8:
                    beat -= 8

        # Create playlist clip
        clip = PlaylistClipData()
        clip.clip.value = 1
        clip.type.value = "MIDI"
        data.playlist_clips.add(clip)

        Playlist.instance()
        me = MidiEditor.open(1)

        # Simulate a ui note deletion (like would happen with right-click)
        for n in me.ui_notes:
            n.delete()
            break

        assert len(list(me.ui_notes)) == len(data.midi_clips[1].notes)


def test_midi_editor_paste_note():
    with UiTestSession():
        me = MidiEditor.open(1)
        me.paste_note(100, 100)
        assert len(data.midi_clips[1].notes) == 1


def test_create_unique_clip():
    with UiTestSession():

        for i in range(2):
            clip = PlaylistClipData()
            clip.clip.value = 1
            clip.beat.value = i * 4
            data.playlist_clips.add(clip)

        # This will create a midi clip
        # which will cause make_unique to
        # actually make a new clip
        me = MidiEditor.open(1)
        me.paste_note(100, 100)

        pl = Playlist.instance()
        for c in pl.ui_clips:
            if c.clip.beat.value > 2:
                c.make_unique()

        # There should now be two unique clips in the UI
        assert len({c.clip.clip.value for c in pl.ui_clips}) == 2


def test_create_unique_clip_no_midi():
    with UiTestSession():

        for i in range(2):
            clip = PlaylistClipData()
            clip.clip.value = 1
            clip.beat.value = i * 4
            data.playlist_clips.add(clip)

        pl = Playlist.instance()
        for c in pl.ui_clips:
            if c.clip.beat.value > 2:
                c.make_unique()

        # There should now be two unique clips in the playlist
        assert len({c.clip.clip.value for c in pl.ui_clips}) == 2


def test_open_close_router():
    with UiTestSession() as ts:
        Router.instance()
        qt = ts.main_loop_ms // 4
        add_timeout(Router.clear_instance, qt)
        add_timeout(Router.instance, qt * 2)
        add_timeout(Router.clear_instance, qt * 3)


def test_router_add_track_signals():
    with UiTestSession():
        # Add 16 router components
        rt = Router.instance()
        for x in range(4):
            for y in range(4):
                rt.add_track_signal(x * 100, y * 100)

        # Remove the first two/last one
        data.router_components.pop(0)
        data.router_components.pop(1)
        data.router_components.pop(15)

        assert len(list(rt.components)) == 13


def test_playlist_colors():
    assert not Playlist.instance_exists()

    with UiTestSession(main_loop_ms=500):

        for beat in range(10):
            beat = beat * 4

            for track in range(15):
                plc = PlaylistClipData()
                plc.track.value = track
                plc.clip.value = track
                plc.beat.value = beat

                data.playlist_clips.add(plc)

        Playlist.instance()
