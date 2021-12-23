from jackdaw.Data.DataObjects import *


class ThirdLevel(DataObject):

    def __init__(self):
        self.field_1 = RawDataObject("String")
        self.field_2 = RawDataObject(0)
        self.field_3 = RawDataObject(1.0)


class SecondLevel(DataObject):

    def __init__(self):
        self.field_1 = RawDataObject("String")
        self.field_2 = RawDataObject(0)
        self.field_3 = RawDataObject(1.0)
        self.dict = DataObjectDict(int, ThirdLevel)


class TopLevel(DataObject):

    def __init__(self):
        self.field_1 = SecondLevel()
        self.dict = DataObjectDict(int, SecondLevel)


def get_example():
    data = TopLevel()

    data.dict[0].dict[0].field_1.value = "Modified string"
    assert data.dict[2] is not None

    return data


def test_serialize_deserialize():
    d = get_example()
    d2 = TopLevel()
    d2.deserialize(d.serialize())
    assert d2.serialize() == d.serialize()


def test_serialize_deserialize_json():
    d = get_example()
    d2 = TopLevel()
    d2.deserialize_json(d.pretty_json())
    assert d2.serialize() == d.serialize()


def test_error_nonserializable():
    try:
        RawDataObject(get_example())
    except NotSerializableError:
        return
    assert False
