from ..Utils.JackdawTestSession import JackdawTestSession
from jackdaw.UI.Playlist import Playlist
from jackdaw.UI.MidiEditor import MidiEditor
from jackdaw.Data import data
from jackdaw.Data.ProjectData import \
    MidiNoteData, MidiClipData, PlaylistClipData, \
    RouterComponentData, RouterComponentDataWrapper, RouterRouteData
from jackdaw import MusicTheory
from jackdaw.Gi import add_timeout
from jackdaw.UI.Router import Router
from jackdaw.UI.RouterComponent import RouterComponent, ChannelExistsException
from jackdaw.UI.ControlPanel import ControlPanel
from jackdaw.Gi import Gtk


def test_control_panel():
    with JackdawTestSession():
        ControlPanel.instance()


def test_open_playlist():
    with JackdawTestSession():
        assert Playlist.instance() is not None


def test_open_midi_editor():
    with JackdawTestSession():
        assert MidiEditor.open(1) is not None


def test_open_close_midi_editor():
    with JackdawTestSession():
        for i in range(10):
            assert MidiEditor.open(i) is not None
            MidiEditor.close(i)


def test_open_many_midi_editors():
    with JackdawTestSession() as ts:
        def add_editor():
            number = len(MidiEditor.open_editors) + 1
            assert MidiEditor.open(number) is not None

        add_timeout(add_editor, ts.main_loop_ms // 100, repeats=10)


def test_create_playlist_clips():
    with JackdawTestSession():
        for i in range(100):
            clip = PlaylistClipData()
            clip.beat.value = i % 16
            clip.track.value = i
            data.playlist_clips.add(clip)

        Playlist.instance()


def test_playlist_paste_clip():
    with JackdawTestSession():
        pl = Playlist.instance()
        pl.paste_clip(100, 100)
        assert len(list(pl.ui_clips)) == 1
        assert len(data.playlist_clips) == 1


def test_create_midi_clip():
    with JackdawTestSession():

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
    with JackdawTestSession():
        me = MidiEditor.open(1)
        me.paste_note(100, 100)
        assert len(data.midi_clips[1].notes) == 1


def test_create_unique_clip():
    with JackdawTestSession():

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
    with JackdawTestSession():

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
    with JackdawTestSession() as ts:
        Router.instance()
        qt = ts.main_loop_ms // 4
        add_timeout(Router.clear_instance, qt)
        add_timeout(Router.instance, qt * 2)
        add_timeout(Router.clear_instance, qt * 3)


def test_router_add_track_signals():
    with JackdawTestSession():
        # Add 16 router components
        rt = Router.instance()
        for x in range(4):
            for y in range(4):
                rt.add_component("TrackSignalData", x * 100, y * 100)

        # Remove the first two/last one
        data.router_components.pop(0)
        data.router_components.pop(1)
        data.router_components.pop(15)

        assert len(list(rt.components)) == 13


def test_channel_exists_exception():
    class TestCompData(RouterComponentData):

        def create_component(self, id: int):
            return TestComp(id)

    # Component test class
    class TestComp(RouterComponent):

        init_called = False

        def __init__(self, id: int):
            super().__init__(id)
            self.add_input_channel("input")
            self.add_output_channel("output")

            try:
                self.add_input_channel("input")
                assert False
            except ChannelExistsException:
                pass

            try:
                self.add_output_channel("output")
                assert False
            except ChannelExistsException:
                pass

            TestComp.init_called = True

    with JackdawTestSession():
        # Create a test component
        comp_data = RouterComponentDataWrapper()
        comp_data.datatype.value = "TestCompData"
        comp_id = data.router_components.get_unique_key()
        data.router_components[comp_id] = comp_data

        # Open the router
        Router.instance()

        assert TestComp.init_called


def test_router_connect():
    # Check no components were leftover from previous test
    assert len(data.router_components) == 0

    # Test component data class
    class TestCompData(RouterComponentData):

        def create_component(self, id: int):
            return TestComp(id)

    # Test component class
    class TestComp(RouterComponent):

        def __init__(self, id: int):
            super().__init__(id)
            self.add_input_channel("input")
            self.add_output_channel("output")
            self.content = Gtk.Label(label="Test")

    with JackdawTestSession():

        # Open the router ui
        rt: Router = Router.instance()

        # Create some test components
        ids = list()
        for j in range(0, 4):
            for i in range(0, 4):
                comp_data = RouterComponentDataWrapper()
                comp_data.datatype.value = "TestCompData"
                comp_data.component_data.position.value = (200 * (i + 1), 100 * (1 + j + i % 2))
                comp_id = data.router_components.get_unique_key()
                data.router_components[comp_id] = comp_data
                ids.append(comp_id)
        assert len(data.router_components) == len(ids)

        # Create routing links between components
        for i in range(1, len(ids)):
            if i % 2 == 0:
                # The data way
                route = RouterRouteData()
                route.from_component.value = ids[i - 1]
                route.from_channel.value = "output"
                route.to_component.value = ids[i]
                route.to_channel.value = "input"
                data.routes.add(route)
            else:
                # The UI way
                rt.on_click_routing_node(ids[i - 1], "output", False)
                rt.on_click_routing_node(ids[i], "input", True)
        assert len(data.routes) == len(ids) - 1

        # Destroy the second link the data way
        routes_before = len(data.routes)
        for i, route in enumerate(data.routes):
            if i == 1:
                data.routes.remove(route)
                break
        assert len(data.routes) == routes_before - 1

        # Destroy the first link the ui way
        routes_before = len(data.routes)
        rt.on_click_routing_node(ids[0], "output", False)
        rt.on_click_routing_node(ids[1], "input", True)
        assert len(data.routes) == routes_before - 1

        # Destroy some components
        for i, comp_id in enumerate(list(ids)):
            if i % 3 == 0:
                data.router_components.pop(comp_id)
                ids.remove(comp_id)
        assert len(list(rt.components)) == len(ids)


def test_playlist_colors():
    assert not Playlist.instance_exists()

    with JackdawTestSession():

        for beat in range(10):
            beat = beat * 4

            for track in range(15):
                plc = PlaylistClipData()
                plc.track.value = track
                plc.clip.value = track
                plc.beat.value = beat

                data.playlist_clips.add(plc)

        Playlist.instance()
