from jackdaw.Data.DataObjects import *


def get_example():
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
            self.dict = DataObjectDict(ThirdLevel)

    class TopLevel(DataObject):

        def __init__(self):
            self.field_1 = SecondLevel()
            self.dict = DataObjectDict(SecondLevel)

    data = TopLevel()
    data.dict[0].dict[0].field_1.value = "Modified string"
    assert data.dict[2] is not None

    return data


def test_serialize_deserialize():
    d = get_example()
    print(d.pretty_json())
