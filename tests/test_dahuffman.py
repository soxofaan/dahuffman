# coding=utf-8
import io
import re
from io import StringIO
from pathlib import Path

import pytest

from dahuffman import HuffmanCodec
from dahuffman.huffmancodec import PrefixCodec, _EOF


# TODO test streaming


def test_prefix_codec():
    code_table = {'A': (2, 0), 'B': (2, 1), _EOF: (2, 3)}
    codec = PrefixCodec(code_table, check=True)
    encoded = codec.encode('ABBA')
    assert encoded == b'\x14'


@pytest.mark.parametrize('data', [
    "hello world, how are you doing today?",
    b"hello world, how are you doing today?",
    u"hëllò wørl∂, høw åré ¥øü døin§ tø∂@¥?",
])
def test_string_data(data):
    codec = HuffmanCodec.from_data(data)
    encoded = codec.encode(data)
    assert type(encoded) == type(b'')
    assert len(encoded) < len(data)
    decoded = codec.decode(encoded)
    assert decoded == data


@pytest.mark.parametrize('data', [
    [(1, 1), (2, 1), (1, 1), ],
    ['apple', 'pear', 'orange', 'apple', 'lemon', 'pear'],
    [('king', 'w'), ('queen', 'e', 3), ('pawn', 'n'), ('king', 'w')],
])
def test_non_string_symbols(data):
    codec = HuffmanCodec.from_data(data)
    encoded = codec.encode(data)
    assert type(encoded) == type(b'')
    decoded = codec.decode(encoded)
    assert decoded == data


def test_decode_concat():
    codec = HuffmanCodec.from_data([1, 2, 3])
    encoded = codec.encode([1, 2, 1, 2, 3, 2, 1])
    decoded = codec.decode(encoded, concat=sum)
    assert decoded == 12


def test_trailing_zero_handling():
    """
    Just two symbols ('a' and 'b'): without end-of-file handling, each would only take 1 bit (e.g. a=0 and b=1)
    so 'abba' would be 4 bits '0110', trailed with zeros to fill a byte: '0110000', which is indiscernible
    from result of input 'abbaaaaa'. With proper end-of-file handling, trailing bits are ignored properly.
    """
    codec = HuffmanCodec.from_frequencies({'a': 1, 'b': 1})
    decoded = codec.decode(codec.encode('abba'))
    assert decoded == 'abba'


def test_print_code_table():
    codec = HuffmanCodec.from_frequencies({'a': 2, 'b': 4, 'c': 8})
    out = StringIO()
    codec.print_code_table(out=out)
    dump = out.getvalue()
    assert re.search(r"1\s+1\s+.*'c'", dump)
    assert re.search(r"2\s+01\s+.*'b'", dump)
    assert re.search(r"3\s+001\s+.*'a'", dump)
    assert re.search(r"3\s+000\s+.*_EOF", dump)


def test_print_code_table2():
    codec = HuffmanCodec.from_data("aaaaa")
    out = io.StringIO()
    codec.print_code_table(out=out)
    actual = out.getvalue().split('\n')
    expected = "Bits Code Value Symbol\n   1 0        0 _EOF\n   1 1        1 'a'\n".split('\n')
    assert actual[0] == expected[0]
    assert set(actual[1:]) == set(expected[1:])


def test_eof_cut_off():
    # Using frequency table that should give this encoding
    # A   -> 0
    # B   -> 11
    # C   -> 101
    # EOF -> 100
    codec = HuffmanCodec.from_frequencies({'A': 5, 'B': 4, 'C': 2, })
    cases = {
        # Straightforward cases
        '': 0, 'A': 1, 'AB': 1, 'ABB': 1, 'CCC': 2,
        # Cases where EOF cut-off saves one output byte
        'ACC': 1, 'CC': 1,
        'CCCCC': 2,
    }
    for data, expected_length in cases.items():
        encoded = codec.encode(data)
        assert len(encoded) == expected_length
        assert data == codec.decode(encoded)


def test_save(tmp_path: Path):
    codec1 = HuffmanCodec.from_data('aabcbcdbabdbcbd')
    path = str(tmp_path / 'foo' / 'bar.huff')
    codec1.save(path)
    output1 = codec1.encode('abcdabcd')
    codec2 = PrefixCodec.load(path)
    output2 = codec2.encode('abcdabcd')
    assert output1 == output2
    assert codec1.decode(output1) == codec2.decode(output2)
