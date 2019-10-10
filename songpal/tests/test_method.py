import pytest
from songpal.method import Method, MethodSignature
from songpal import SongpalException


def test_methodsignature_rettype():
    assert MethodSignature.return_type("string") == str
    assert MethodSignature.return_type("Boolean") == bool
    assert MethodSignature.return_type("int") == int

    # return input when not matching.
    assert MethodSignature.return_type("foofoo") == "foofoo"


def test_methodsignature_parse_json_types():
    assert False


def test_methodsignature_serialize_types():
    # None stays None
    assert MethodSignature._serialize_types(None) == None

    types_to_test = {'str_test': str,
                     'int_test': int}
    res = MethodSignature._serialize_types(types_to_test)
    assert len(res) == len(types_to_test)
    assert res["str_test"] == "str"
    assert res["int_test"] == "int"


def test_method_call_failed():
    with pytest.raises(SongpalException):
        print("when communication with the device fails "
              "this exception should be raised and the error "
              "attribute should be kept empty?")


def test_method_call_error_from_device():
    with pytest.raises(SongpalException):
        print("when service.call_method result contains error, "
              "this exception should be reaised and its error attribute"
              " should be set")


def test_method_serialize_types():
    assert False
