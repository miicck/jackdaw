import os
from jackdaw.Data.DataObjects import *
from jackdaw.Utils.Singleton import Singleton


# This file contains the specification
# of the project data hierarchy

class MidiNoteData(DataObject):

    def __init__(self):
        self.note = RawDataObject("C3")
        self.beat = RawDataObject(0.0)


class MidiClipData(DataObject):

    def __init__(self):
        self.notes = DataObjectSet(MidiNoteData)


class PlaylistClipData(DataObject):

    def __init__(self):
        self.clip = RawDataObject(0)
        self.track = RawDataObject(0)
        self.beat = RawDataObject(0.0)
        self.type = RawDataObject("MIDI")


class RouterComponentData(DataObject):

    def __init__(self):
        self.position = RawDataObject((100, 100))

    def create_component(self, id: int):
        raise Exception("Tried to create a router component from uninitialized data!")

    @classmethod
    def diaply_name(cls):
        return cls.__name__.replace("Data", "")


class RouterComponentDataWrapper(DataObject):

    def __init__(self):
        self.datatype = RawDataObject("Unknown data type")
        self.component_data = RouterComponentData()
        self.datatype.add_on_change_listener(self.set_datatype)

    def set_datatype(self):
        for c in RouterComponentData.__subclasses__():
            if c.__name__ == self.datatype.value:
                if isinstance(self.component_data, c):
                    return  # Already of correct type
                if not isinstance(self.component_data, RouterComponentData):
                    raise Exception("Tried to overwrite component data with different type!")
                self.component_data = c()
                return
        raise Exception(f"Unknown component datatype \"{self.datatype.value}\"")

    def deserialize(self, data: dict) -> None:
        self.datatype.value = data["datatype"]
        super().deserialize(data)


class RouterRouteData(DataObject):

    def __init__(self):
        self.from_component = RawDataObject(-1)
        self.from_channel = RawDataObject("Unknown channel")
        self.to_component = RawDataObject(-1)
        self.to_channel = RawDataObject("Unknown channel")


class ProjectData(Singleton, DataObject):

    def __init__(self):
        DataObject.__init__(self)
        Singleton.__init__(self)

        # Setup data components
        self.midi_clips = DataObjectDict(int, MidiClipData)
        self.playlist_clips = DataObjectSet(PlaylistClipData)
        self.router_components = DataObjectDict(int, RouterComponentDataWrapper)
        self.routes = DataObjectSet(RouterRouteData)

        self.load()

    def save(self):
        with open(ProjectData.FILENAME, "w") as f:
            self.write_pretty_json_file(f)
            f.flush()

    def load(self):
        if os.path.isfile(ProjectData.FILENAME):
            with open(ProjectData.FILENAME, "r") as f:
                self.deserialize_from_json_file(f)

    def on_clear_singleton_instance(self):
        self.save()

    def empty_project_assertions(self):
        assert len(self.midi_clips) == 0
        assert len(self.playlist_clips) == 0
        assert len(self.router_components) == 0
        assert len(self.routes) == 0

    ################
    # STATIC STUFF #
    ################

    FILENAME = "ProjectData.json"
