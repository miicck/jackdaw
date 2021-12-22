from jackdaw.RuntimeChecks import must_be_called_from, CallStructureException


def test_must_be_called_from():
    def function_1():
        function_2()

    def function_2():
        must_be_called_from(function_1)

    function_1()

    exception = False
    try:
        function_2()
    except CallStructureException:
        exception = True

    assert exception
