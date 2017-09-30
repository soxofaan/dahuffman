# coding=utf-8
import dahuffman

import pytest


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

# TODO tox for py3
