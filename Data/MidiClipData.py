from Data import Filestructure as FS
from Data.MidiNoteData import MidiNoteData
from Session import session_close_method
from Data.LineSerializable import LineSerializableCollection
from typing import List


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
        return f"{FS.DATA_DIR}/midi/{self._clip_number}.jdm"

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
    def unload_all_clips():
        """
        Call to unload all loaded clips.
        :return:
        """
        MidiClipData._loaded_clips = dict()
