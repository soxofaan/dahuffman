"""

This folder contains a bunch of pre-trained
HuffmanCodec code tables.

"""

from functools import partial
from pathlib import Path

import pkg_resources

from dahuffman.huffmancodec import PrefixCodec


def load(name: str) -> PrefixCodec:
    """
    Load a pre-trained PrefixCodec or HuffmanCodec table by name

    >>> load("shakespeare")
    <dahuffman.huffmancodec.HuffmanCodec object at 0x107fe5b70>
    """
    return PrefixCodec.load(get_path(name))


def get_path(name: str) -> Path:
    if not name.endswith('.pickle'):
        name = name + '.pickle'
    path = pkg_resources.resource_filename('dahuffman', 'codecs/' + name)
    return Path(path)


load_shakespeare = partial(load, "shakespeare")
load_shakespeare_lower = partial(load, "shakespeare-lower")
load_json = partial(load, "json")
load_json_compact = partial(load, "json-compact")
load_xml = partial(load, "xml")
