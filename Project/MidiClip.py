from Project import Filestructure as FS
from Project.MidiNote import MidiNote
from typing import List, Callable
import os
from Session import session_close_method


class MidiClip:

    def __init__(self, clip_number: int):
        """
        A MIDI clip data object, linked to a clip number.
        :param clip_number: The MIDI clip number.
        """
        self.filename = f"{FS.DATA_DIR}/midi/{clip_number}.jdm"
        self._clip_number = clip_number
        self._notes = []
        self._on_change_listeners = []

        # Attempt to load the clip
        self.load()

    def save(self) -> None:
        """
        Saves all of my notes to file.
        :return: None
        """
        os.makedirs(os.path.dirname(self.filename), exist_ok=True)
        with open(self.filename, "w") as f:
            for n in self.notes:
                f.write(n.save_to_line() + "\n")

    def load(self) -> None:
        """
        Load my notes from file.
        :return: None
        """
        self._notes = []
        if os.path.isfile(self.filename):
            with open(self.filename, "r") as f:
                for line in f:
                    self._notes.append(MidiNote.load_from_line(line))
        self.invoke_on_change_listeners()

    def add_note(self, note: MidiNote) -> None:
        """
        Adds a note to this clip.
        :param note: The note to add.
        :return: None.
        """
        self._notes.append(note)
        self.invoke_on_change_listeners()

    def remote_note(self, note: MidiNote) -> None:
        """
        Removes a note from this clip.
        :param note: The note to remove.
        :return: None.
        """
        if note not in self._notes:
            raise Exception("Note to remove not found in clip!")
        self._notes.remove(note)
        self.invoke_on_change_listeners()

    def invoke_on_change_listeners(self) -> None:
        """
        Invokes all listeners added via add_change_listener.
        :return: None
        """
        for c in self._on_change_listeners:
            c(self)
        self.save()

    def add_change_listener(self, callback: Callable[['MidiNote'], None]):
        """
        Add a listener to be called whenever this clip might have changed.
        :param callback: The listener to call.
        :return: None
        """
        self._on_change_listeners.append(callback)

    ##############
    # PROPERTIES #
    ##############

    @property
    def clip_number(self) -> int:
        return self._clip_number

    @property
    def notes(self) -> List[MidiNote]:
        return [n for n in self._notes]

    ################
    # STATIC STUFF #
    ################

    _loaded_clips = dict()

    @staticmethod
    def get(clip_number: int) -> 'MidiClip':
        """
        :param clip_number: The MIDI clip number.
        :return: The MIDI data associated with the given clip number.
        :rtype: MidiClip
        """
        # Load existing clip
        if clip_number in MidiClip._loaded_clips:
            clip = MidiClip._loaded_clips[clip_number]
            assert clip.clip_number == clip_number
            return clip

        # Create new clip
        new_clip = MidiClip(clip_number)
        MidiClip._loaded_clips[clip_number] = new_clip
        return new_clip

    @staticmethod
    @session_close_method
    def unload_all_clips():
        """
        Call to unload all loaded clips.
        :return:
        """
        MidiClip._loaded_clips = dict()
