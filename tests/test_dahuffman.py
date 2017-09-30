# coding=utf-8
import StringIO
import re

import pytest

import dahuffman


@pytest.mark.parametrize('data', [
    "hello world, how are you doing today?",
    b"hello world, how are you doing today?",
    u"hëllò wørl∂, høw åré ¥øü døin§ tø∂@¥?",
])
def test_string_data(data):
    codec = dahuffman.HuffmanCodec.from_data(data)
    encoded = codec.encode(data)
    assert type(encoded) == type(b'')
    assert len(encoded) < len(data)
    decoded = codec.decode(encoded)
    assert decoded == data


@pytest.mark.parametrize('data', [
    [(1, 1), (2, 1), (1, 1), ],
    ['apple', 'pear', 'orange', 'apple', 'lemon', 'pear'],
    [('king', 'w'), ('queen', 'e', 3), ('pawn', 'n'), ('king', 'w')],
    [None, (), None, (None, None), None],
])
def test_non_string_symbols(data):
    codec = dahuffman.HuffmanCodec.from_data(data)
    encoded = codec.encode(data)
    assert type(encoded) == type(b'')
    decoded = codec.decode(encoded, as_list=True)
    assert decoded == data


def test_trailing_zero_handling():
    """
    Just two symbols ('a' and 'b'): without end-of-file handling, each would only take 1 bit (e.g. a=0 and b=1)
    so 'abba' would be 4 bits '0110', trailed with zeros to fill a byte: '0110000', which is indiscernible
    from result of input 'abbaaaaa'. With proper end-of-file handling, trailing bits are ignored properly.
    """
    codec = dahuffman.HuffmanCodec({'a': 1, 'b': 1})
    decoded = codec.decode(codec.encode('abba'))
    assert decoded == 'abba'


def test_dump():
    codec = dahuffman.HuffmanCodec({'a': 2, 'b': 4, 'c': 8})
    out = StringIO.StringIO()
    codec.dump(out=out)
    dump = out.getvalue()
    assert re.search(r"1\s+1\s+.*'c'", dump)
    assert re.search(r"2\s+01\s+.*'b'", dump)
    assert re.search(r"3\s+001\s+.*'a'", dump)
    assert re.search(r"3\s+000\s+.*_EOF", dump)

# TODO tox for py3
