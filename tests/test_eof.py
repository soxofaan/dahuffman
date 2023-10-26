import pytest

from dahuffman.huffmancodec import _EOF


def test_eq():
    assert _EOF == _EOF


@pytest.fixture(params=(b'a', b'\0', b'_EOF'))
def raw_value(request):
    return request.param


@pytest.fixture(params=(lambda b: b.decode('utf-8'), bytes, tuple))
def of_type(request):
    return request.param


@pytest.fixture
def to_compare(raw_value, of_type):
    return of_type(raw_value)


def test_lt(to_compare):
    assert _EOF < to_compare


def test_gt(to_compare):
    assert to_compare > _EOF
