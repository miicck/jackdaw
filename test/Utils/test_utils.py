from .JackdawTestSession import JackdawTestSession
from jackdaw.Data.ProjectData import ProjectData
from jackdaw.Utils.Singleton import Singleton, SingletonException


def test_ui_closed_properly():
    with JackdawTestSession():
        pass

    assert not ProjectData.instance_exists()


def test_singleton():
    class Test1(Singleton):
        pass

    class Test2(Singleton):
        pass

    class Test3(Test2, Singleton):
        pass

    class Test4(Test2):
        pass

    try:
        Test1()
        assert False
    except SingletonException:
        pass

    a = Test1.instance()
    b = Test1.instance()
    assert a == b

    c = Test2.instance()
    d = Test2.instance()
    assert c == d
    assert a != c

    e = Test3.instance()
    assert e == c

    f = Test4.instance()
    assert f == c
