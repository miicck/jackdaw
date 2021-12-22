from ..Utils.UiTestSession import UiTestSession
from jackdaw.UI.Playlist import Playlist
from jackdaw.UI.MidiEditor import MidiEditor
from jackdaw.Data.MidiNoteData import MidiNoteData
from jackdaw.Data.MidiClipData import MidiClipData
from jackdaw import MusicTheory
from jackdaw.Data.PlaylistClipData import PlaylistClipData
from jackdaw.Gi import add_timeout
from jackdaw.UI.Router import Router


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
    with UiTestSession() as ts:
        def add_editor():
            number = len(MidiEditor.open_editors) + 1
            assert MidiEditor.open(number) is not None

        add_timeout(add_editor, ts.main_loop_ms // 100, repeats=10)


def test_create_playlist_clips():
    with UiTestSession():
        pl = Playlist.open()
        for i in range(100):
            pl.data.add(PlaylistClipData(i, i, i % 16))


def test_create_midi_clip():
    with UiTestSession():
        pl = Playlist.open()
        pl.data.add(PlaylistClipData(1, 0, 0))
        me = MidiEditor.open(1)

        beat = 0
        for octave in range(0, MidiEditor.MAX_OCTAVE + 1):
            for note in MusicTheory.NOTES:

                me.clip.add(MidiNoteData(f"{note}{octave}", beat))

                beat += 0.25
                if beat > 8:
                    beat -= 8

        try:
            me.clip.add(MidiNoteData("C50", 0))
        except MidiEditor.NoteOutOfRangeException as e:
            assert True


def test_create_unique_clip():
    with UiTestSession():
        pl = Playlist.open()
        pl.data.add(PlaylistClipData(1, 0, 0))
        pl.data.add(PlaylistClipData(1, 0, 4))
        me = MidiEditor.open(1)
        me.clip.add(MidiNoteData("C3", 0))

        # There should be just one clip on disk
        assert len(list(MidiClipData.clips_on_disk())) == 1

        for c in pl.ui_clips:
            if c.clip.beat > 2:
                c.make_unique()

        # There should now be two clips in the UI/on disk
        assert len({c.clip.clip_number for c in pl.ui_clips}) == 2
        assert len(list(MidiClipData.clips_on_disk())) == 2


def test_create_unique_clip_no_midi():
    with UiTestSession():
        pl = Playlist.open()
        pl.data.add(PlaylistClipData(1, 0, 0))
        pl.data.add(PlaylistClipData(1, 0, 4))

        # No midi files should have been created yet
        assert len(list(MidiClipData.clips_on_disk())) == 0

        for c in pl.ui_clips:
            if c.clip.beat > 2:
                c.make_unique()

        # Because no midi clips existed, make_unique shouldn't do anything
        # => there should only be one unique clip in the playlist
        # and no midi should have been created on disk
        assert len({c.clip.clip_number for c in pl.ui_clips}) == 1
        assert len(list(MidiClipData.clips_on_disk())) == 0


def test_open_close_router():
    with UiTestSession() as ts:
        Router.open()
        qt = ts.main_loop_ms // 4
        add_timeout(Router.close, qt)
        add_timeout(Router.open, qt * 2)
        add_timeout(Router.close, qt * 3)


def test_router_add_track_signals():
    with UiTestSession():
        rt = Router.open()
        for x in range(1, 10):
            for y in range(1, 10):
                rt.add_track_signal(x * 100, y * 100)