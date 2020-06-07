import collections
import itertools
import sys
from heapq import heappush, heappop, heapify

import logging
import pickle
from pathlib import Path
from typing import Union, Any

_log = logging.getLogger(__name__)


class _EndOfFileSymbol:
    """
    Internal class for "end of file" symbol to be able
    to detect the end of the encoded bit stream,
    which does not necessarily align with byte boundaries.
    """

    def __repr__(self):
        return '_EOF'

    # Because _EOF will be compared with normal symbols (strings, bytes),
    # we have to provide a minimal set of comparison methods.
    # We'll make _EOF smaller than the rest (meaning lowest frequency)
    def __lt__(self, other):
        return True

    def __gt__(self, other):
        return False

    def __eq__(self, other):
        return other.__class__ == self.__class__

    def __hash__(self):
        return hash(self.__class__)


# Singleton-like "end of file" symbol
_EOF = _EndOfFileSymbol()


# TODO store/load code table from file
# TODO Directly encode to and decode from file

def _guess_concat(data):
    """
    Guess concat function from given data
    """
    return {
        type(u''): u''.join,
        type(b''): bytes,
    }.get(type(data), list)


def ensure_dir(path: Union[str, Path]) -> Path:
    path = Path(path)
    if not path.exists():
        path.mkdir(parents=True)
    assert path.is_dir()
    return path


class PrefixCodec:
    """
    Prefix code codec, using given code table.
    """

    def __init__(self, code_table, concat=list, check=True, eof=_EOF):
        """
        Initialize codec with given code table.

        :param code_table: mapping of symbol to code tuple (bitsize, value)
        :param concat: function to concatenate symbols
        :param check: whether to check the code table
        :param eof: "end of file" symbol (customizable for advanced usage)
        """
        # Code table is dictionary mapping symbol to (bitsize, value)
        self._table = code_table
        self._concat = concat
        self._eof = eof
        if check:
            assert isinstance(self._table, dict) and all(
                isinstance(b, int) and b >= 1 and isinstance(v, int) and v >= 0
                for (b, v) in self._table.values()
            )
            # TODO check if code table is actually a prefix code

    def get_code_table(self):
        """
        Get code table
        :return: dictionary mapping symbol to code tuple (bitsize, value)
        """
        return self._table

    def print_code_table(self, out=sys.stdout):
        """
        Print code table overview
        """
        # TODO: add sort options?
        # Render table cells as string
        columns = list(zip(*itertools.chain(
            [('Bits', 'Code', 'Value', 'Symbol')],
            (
                (str(bits), bin(val)[2:].rjust(bits, '0'), str(val), repr(symbol))
                for symbol, (bits, val) in self._table.items()
            )
        )))
        # Find column widths and build row template
        widths = tuple(max(len(s) for s in col) for col in columns)
        template = '{0:>%d} {1:%d} {2:>%d} {3}\n' % widths[:3]
        for row in zip(*columns):
            out.write(template.format(*row))

    def encode(self, data):
        """
        Encode given data.

        :param data: sequence of symbols (e.g. byte string, unicode string, list, iterator)
        :return: byte string
        """
        return bytes(self.encode_streaming(data))

    def encode_streaming(self, data):
        """
        Encode given data in streaming fashion.

        :param data: sequence of symbols (e.g. byte string, unicode string, list, iterator)
        :return: generator of bytes (single character strings in Python2, ints in Python 3)
        """
        # Buffer value and size
        buffer = 0
        size = 0
        for s in data:
            # TODO: raise custom EncodeException instead of KeyError?
            b, v = self._table[s]
            # Shift new bits in the buffer
            buffer = (buffer << b) + v
            size += b
            while size >= 8:
                byte = buffer >> (size - 8)
                yield byte
                buffer = buffer - (byte << (size - 8))
                size -= 8

        # Handling of the final sub-byte chunk.
        # The end of the encoded bit stream does not align necessarily with byte boundaries,
        # so we need an "end of file" indicator symbol (_EOF) to guard against decoding
        # the non-data trailing bits of the last byte.
        # As an optimization however, while encoding _EOF, it is only necessary to encode up to
        # the end of the current byte and cut off there.
        # No new byte has to be started for the remainder, saving us one (or more) output bytes.
        if size > 0:
            b, v = self._table[self._eof]
            buffer = (buffer << b) + v
            size += b
            if size >= 8:
                byte = buffer >> (size - 8)
            else:
                byte = buffer << (8 - size)
            yield byte

    def decode(self, data, concat=None):
        """
        Decode given data.

        :param data: sequence of bytes (string, list or generator of bytes)
        :param concat: optional override of function to concatenate the decoded symbols
        :return:
        """
        return (concat or self._concat)(self.decode_streaming(data))

    def decode_streaming(self, data):
        """
        Decode given data in streaming fashion

        :param data: sequence of bytes (string, list or generator of bytes)
        :return: generator of symbols
        """
        # Reverse lookup table: map (bitsize, value) to symbols
        lookup = {(b, v): s for s, (b, v) in self._table.items()}

        buffer = 0
        size = 0
        for byte in data:
            for m in [128, 64, 32, 16, 8, 4, 2, 1]:
                buffer = (buffer << 1) + bool(byte & m)
                size += 1
                if (size, buffer) in lookup:
                    symbol = lookup[size, buffer]
                    if symbol == self._eof:
                        return
                    yield symbol
                    buffer = 0
                    size = 0

    def save(self, path: Union[str, Path], metadata: Any = None):
        """
        Persist the code table to a file.
        :param path: file path to persist to
        :param metadata: additional metadata
        :return:
        """
        code_table = self.get_code_table()
        data = {
            "code_table": code_table,
            "type": type(self),
            "concat": self._concat,
        }
        if metadata:
            data['metadata'] = metadata
        path = Path(path)
        ensure_dir(path.parent)
        with path.open(mode='wb') as f:
            # TODO also provide JSON option? Requires handling of _EOF and possibly other non-string code table keys.
            pickle.dump(data, file=f)
        _log.info('Saved {c} code table ({l} items) to {p!r}'.format(
            c=type(self).__name__, l=len(code_table), p=str(path)
        ))

    @staticmethod
    def load(path: Union[str, Path]) -> 'PrefixCodec':
        """
        Load a persisted PrefixCodec
        :param path: path to serialized PrefixCodec code table data.
        :return:
        """
        path = Path(path)
        with path.open(mode='rb') as f:
            data = pickle.load(f)
        cls = data['type']
        assert issubclass(cls, PrefixCodec)
        code_table = data['code_table']
        _log.info('Loading {c} with {l} code table items from {p!r}'.format(
            c=cls.__name__, l=len(code_table), p=str(path)
        ))
        return cls(code_table, concat=data['concat'])


class HuffmanCodec(PrefixCodec):
    """
    Huffman coder, with code table built from given symbol frequencies or raw data,
    providing encoding and decoding methods.
    """

    @classmethod
    def from_frequencies(cls, frequencies, concat=None, eof=_EOF):
        """
        Build Huffman code table from given symbol frequencies
        :param frequencies: symbol to frequency mapping
        :param concat: function to concatenate symbols
        :param eof: "end of file" symbol (customizable for advanced usage)
        """
        concat = concat or _guess_concat(next(iter(frequencies)))

        # Heap consists of tuples: (frequency, [list of tuples: (symbol, (bitsize, value))])
        heap = [(f, [(s, (0, 0))]) for s, f in frequencies.items()]
        # Add EOF symbol.
        if eof not in frequencies:
            heap.append((1, [(eof, (0, 0))]))

        # Use heapq approach to build the encodings of the huffman tree leaves.
        heapify(heap)
        while len(heap) > 1:
            # Pop the 2 smallest items from heap
            a = heappop(heap)
            b = heappop(heap)
            # Merge nodes (update codes for each symbol appropriately)
            merged = (
                a[0] + b[0],
                [(s, (n + 1, v)) for (s, (n, v)) in a[1]]
                + [(s, (n + 1, (1 << n) + v)) for (s, (n, v)) in b[1]]
            )
            heappush(heap, merged)

        # Code table is dictionary mapping symbol to (bitsize, value)
        table = dict(heappop(heap)[1])

        return cls(table, concat=concat, check=False, eof=eof)

    @classmethod
    def from_data(cls, data):
        """
        Build Huffman code table from symbol sequence

        :param data: sequence of symbols (e.g. byte string, unicode string, list, iterator)
        :return: HuffmanCoder
        """
        frequencies = collections.Counter(data)
        return cls.from_frequencies(frequencies, concat=_guess_concat(data))
