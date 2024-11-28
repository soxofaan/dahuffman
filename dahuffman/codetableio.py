"""
Functionality to save/load a code table to/from a file
"""

import json
import logging
import pickle
from pathlib import Path
from typing import Any, Optional, Union

from dahuffman.huffmancodec import _EOF, PrefixCodec

_log = logging.getLogger(__name__)


def ensure_dir(path: Union[str, Path]) -> Path:
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def pickle_save(
    codec: PrefixCodec, path: Union[str, Path], metadata: Any = None
) -> None:
    """
    Persist the code table to a file.

    :param path: file path to persist to
    :param metadata: additional metadata to include
    """
    code_table = codec.get_code_table()
    data = {
        "code_table": code_table,
        "type": type(codec),
        "concat": codec._concat,
    }
    if metadata:
        data["metadata"] = metadata
    path = Path(path)
    ensure_dir(path.parent)
    with path.open(mode="wb") as f:
        pickle.dump(data, file=f)
    _log.info(
        f"Saved {type(codec).__name__} code table ({len(code_table)} items) to {str(path)!r}"
    )


def pickle_load(path: Union[str, Path]) -> PrefixCodec:
    """
    Load a persisted PrefixCodec
    :param path: path to serialized PrefixCodec code table data.
    """
    path = Path(path)
    with path.open(mode="rb") as f:
        data = pickle.load(f)
    cls = data["type"]
    assert issubclass(cls, PrefixCodec)
    code_table = data["code_table"]
    _log.info(
        f"Loading {cls.__name__} with {len(code_table)} code table items from {str(path)!r}"
    )
    return cls(code_table, concat=data["concat"])


def json_save(
    codec: PrefixCodec, path: Union[str, Path], metadata: Optional[dict] = None
) -> None:
    """
    Persist the code table as a JSON file.
    Requires that all structures in the code table are JSON-serializable.

    :param path: file path to persist to
    :param metadata: additional metadata to include in the file.
    """
    code_table = codec.get_code_table()

    # Extract internal _EOF symbol from code table
    if _EOF in code_table:
        eof_code = code_table.pop(_EOF)
    else:
        eof_code = None

    # Transform code table dictionary to a list, to avoid string-coercion of keys in JSON mappings.
    code_table = [[k, *v] for (k, v) in code_table.items()]

    data = {
        "type": "dahuffman code table",
        "version": 1,
        "code_table": code_table,
    }
    if eof_code:
        data["eof_code"] = eof_code
    if metadata:
        data["metadata"] = metadata
    if codec._concat == list:
        data["concat"] = "list"
    elif codec._concat == "".join:
        data["concat"] = "str_join"
    elif codec._concat == bytes:
        data["concat"] = "bytes"
    else:
        _log.warning(f"Unsupported concat callable {codec._concat!r}")

    path = Path(path)
    ensure_dir(path.parent)
    with path.open("w", encoding="utf8") as f:
        json.dump(obj=data, fp=f, indent=None, separators=(",", ":"))
    _log.info(
        f"Saved {type(codec).__name__} code table ({len(code_table)} items) to {str(path)!r}"
    )


def json_load(path: Union[str, Path]) -> PrefixCodec:
    path = Path(path)
    with path.open(mode="r", encoding="utf8") as f:
        data = json.load(fp=f)

    assert data["type"] == "dahuffman code table"
    assert data["version"] == 1

    # Reconstruct code table
    code_table = {row[0]: row[1:] for row in data["code_table"]}

    if "eof_code" in data:
        code_table[_EOF] = data["eof_code"]

    concat = {"str_join": "".join, "bytes": bytes}.get(data["concat"], list)

    _log.info(
        f"Loading PrefixCodec with {len(code_table)} code table items from {str(path)!r}"
    )
    return PrefixCodec(code_table, concat=concat)
