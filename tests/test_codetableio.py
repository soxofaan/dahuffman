from pathlib import Path

import pytest

from dahuffman.codetableio import json_load, json_save, pickle_load, pickle_save
from dahuffman.huffmancodec import HuffmanCodec


@pytest.mark.parametrize(
    ["train_data", "data"],
    [
        ("aabcbcdbabdbcbd", "abcdabcd"),
        (
            ["FR", "UK", "BE", "IT", "FR", "IT", "GR", "FR", "NL", "BE", "DE"],
            ["FR", "IT", "BE", "FR", "UK"],
        ),
        (b"aabcbcdbabdbcbd", b"abcdabcd"),
        (
            [(0, 0), (0, 1), (1, 0), (0, 0), (1, 0), (1, 0)],
            [(1, 0), (0, 0), (0, 1), (1, 0)],
        ),
    ],
)
def test_pickle_save_and_load(tmp_path: Path, train_data, data):
    codec1 = HuffmanCodec.from_data(train_data)
    encoded1 = codec1.encode(data)

    path = tmp_path / "code-table.pickle"
    pickle_save(codec=codec1, path=path)
    codec2 = pickle_load(path)
    encoded2 = codec2.encode(data)

    assert encoded1 == encoded2
    assert codec1.decode(encoded1) == codec2.decode(encoded2)


@pytest.mark.parametrize(
    ["train_data", "data"],
    [
        ("aabcbcdbabdbcbd", "abcdabcd"),
        (
            ["FR", "UK", "BE", "IT", "FR", "IT", "GR", "FR", "NL", "BE", "DE"],
            ["FR", "IT", "BE", "FR", "UK"],
        ),
        (b"aabcbcdbabdbcbd", b"abcdabcd"),
        # TODO:
        # (
        #     [(0, 0), (0, 1), (1, 0), (0, 0), (1, 0), (1, 0)],
        #     [(1, 0), (0, 0), (0, 1), (1, 0)],
        # ),
    ],
)
def test_json_save_and_load(tmp_path: Path, train_data, data):
    codec1 = HuffmanCodec.from_data(train_data)
    encoded1 = codec1.encode(data)

    path = tmp_path / "code-table.json"
    json_save(codec=codec1, path=path)
    codec2 = json_load(path)
    encoded2 = codec2.encode(data)

    assert encoded1 == encoded2
    assert codec1.decode(encoded1) == codec2.decode(encoded2)
