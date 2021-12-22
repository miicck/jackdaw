import os
from jackdaw.Data import Filestructure as FS
from jackdaw.Data.MidiNoteData import MidiNoteData
from jackdaw.Session import session_close_method
from jackdaw.Data.LineSerializable import LineSerializableCollection
from typing import List, Iterable


class MidiClipData(LineSerializableCollection[MidiNoteData]):

    def __init__(self, clip_number: int):
        """
        A MIDI clip data object, linked to a clip number.
        :param clip_number: The MIDI clip number.
        """
        super().__init__()

        self._clip_number = clip_number

        # Load the clip if it exists already
        self.load(MidiNoteData.load_from_line)

    @property
    def filename(self) -> str:
        return f"{MidiClipData.midi_directory()}/{self._clip_number}.jdm"

    ##############
    # PROPERTIES #
    ##############

    @property
    def clip_number(self) -> int:
        return self._clip_number

    @property
    def notes(self) -> List[MidiNoteData]:
        return self.data

    ################
    # STATIC STUFF #
    ################

    _loaded_clips = dict()

    @staticmethod
    def get(clip_number: int) -> 'MidiClipData':
        """
        :param clip_number: The MIDI clip number.
        :return: The MIDI data associated with the given clip number.
        :rtype: MidiClipData
        """
        # Load existing clip
        if clip_number in MidiClipData._loaded_clips:
            clip = MidiClipData._loaded_clips[clip_number]
            assert clip.clip_number == clip_number
            return clip

        # Create new clip
        new_clip = MidiClipData(clip_number)
        MidiClipData._loaded_clips[clip_number] = new_clip
        return new_clip

    @staticmethod
    @session_close_method
    def unload_all_clips() -> None:
        """
        Call to unload all loaded clips.
        """
        MidiClipData._loaded_clips = dict()

    @staticmethod
    def midi_directory():
        return f"{FS.DATA_DIR}/midi"

    @staticmethod
    def clips_on_disk() -> Iterable[int]:
        """
        Get all the clip numbers currently defined on disk.
        """
        if os.path.isdir(MidiClipData.midi_directory()):
            for f in os.listdir(MidiClipData.midi_directory()):
                yield int(f.replace(".jdm", ""))
