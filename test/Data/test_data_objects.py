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
        self.list = DataObjectList(SecondLevel)
        self.set = DataObjectSet(SecondLevel)


def get_example():
    data = TopLevel()

    data.dict[0] = SecondLevel()
    data.dict[0].dict[0] = ThirdLevel()
    data.dict[0].dict[0].field_1.value = "Modified string"
    assert data.dict[0].dict[0].field_1.value == "Modified string"

    in_list = SecondLevel()
    data.list.append(in_list)
    assert in_list in data.list
    assert data.list[0] == in_list

    in_set = SecondLevel()
    data.set.add(in_set)
    assert in_set in data.set

    not_in_set = SecondLevel()
    data.set.add(not_in_set)
    data.set.remove(not_in_set)
    assert not_in_set not in data.set

    data.dict[2] = SecondLevel()
    assert data.dict[2] is not None
    return data


def test_get_example():
    assert get_example() is not None


def test_dict_key_type_mismatch_exception():
    d = DataObjectDict(int, ThirdLevel)
    try:
        val = d[1.0]
        assert False
    except TypeMismatchException:
        pass


def test_type_change_exception():
    try:
        # Should throw, setting field rather than field.value
        data_obj = ThirdLevel()
        data_obj.field_1 = 1.0
        assert False
    except TypeMismatchException:
        pass

    try:
        # Should trow, trying to cast float -> int
        data_obj = ThirdLevel()
        data_obj.field_2.value = 1.1
        assert False
    except TypeMismatchException:
        pass

    # Should not throw because casting int -> float
    data_obj = ThirdLevel()
    data_obj.field_3.value = 1


def test_serialize_deserialize():
    d = get_example()
    d2 = TopLevel()
    d2.deserialize(d.serialize())
    assert d2.serialize() == d.serialize()


def test_serialize_deserialize_json():
    d = get_example()
    d2 = TopLevel()
    d2.deserialize_from_json_str(d.get_pretty_json_string())
    assert d2.serialize() == d.serialize()


def test_error_nonserializable():
    try:
        RawDataObject(get_example())
    except NotSerializableError:
        return
    assert False
