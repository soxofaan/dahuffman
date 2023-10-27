import pytest

from dahuffman.huffmancodec import _EOF


def test_eq():
    assert _EOF == _EOF


@pytest.fixture(params=(
    b"\0",
    b"abc",
    "abc",
    0,
    100,
    -1000,
    False,
    True,
    None,
    [],
    (),
    {},
    [-100, 0, 10],
    (-100, 10))
)
def to_compare(request):
    return request.param


def test_lt(to_compare):
    assert _EOF < to_compare


def test_gt(to_compare):
    assert to_compare > _EOF
