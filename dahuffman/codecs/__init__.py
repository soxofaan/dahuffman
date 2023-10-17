"""

This folder contains a bunch of pre-trained
HuffmanCodec code tables.

"""

import importlib.resources
from functools import partial
from pathlib import Path

from dahuffman.huffmancodec import PrefixCodec


def load(name: str) -> PrefixCodec:
    """
    Load a pre-trained PrefixCodec or HuffmanCodec table by name

    >>> load("shakespeare")
    <dahuffman.huffmancodec.HuffmanCodec object at 0x107fe5b70>
    """
    if not name.endswith(".pickle"):
        name = name + ".pickle"
    with importlib.resources.path("dahuffman.codecs", resource=name) as path:
        return PrefixCodec.load(path)



load_shakespeare = partial(load, "shakespeare")
load_shakespeare_lower = partial(load, "shakespeare-lower")
load_json = partial(load, "json")
load_json_compact = partial(load, "json-compact")
load_xml = partial(load, "xml")
