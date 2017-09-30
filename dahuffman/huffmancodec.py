import collections
import itertools
import sys
from heapq import heappush, heappop, heapify

# Oneliner to create singleton end-of-file symbol object
_EOF = type('EOF', (object,), {'__repr__': lambda self: '_EOF'})()


class HuffmanCodec(object):
    """
    Huffman coder, with code table built from given symbol frequencies or raw data,
    providing encoding and decoding methods.
    """

    def __init__(self, frequencies):
        """
        Build Huffman code table from given symbol frequencies
        :param frequencies: symbol to frequency mapping
        """
        # Heap consists of tuples: (frequency, [list of tuples: (symbol, (bitsize, value))])
        heap = [(f, [(s, (0, 0))]) for s, f in frequencies.iteritems()]
        # Add EOF symbol.
        heap.append((1, [(_EOF, (0, 0))]))

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
        self._table = dict(heappop(heap)[1])

    @classmethod
    def from_data(cls, data):
        """
        Build Huffman code table from symbol sequence

        :param data: sequence of symbols (e.g. byte string, unicode string, list, iterator)
        :return: HuffmanCoder
        """
        frequencies = collections.Counter(data)
        return cls(frequencies)

    def dump(self, out=sys.stdout):
        """
        Dump code table
        """
        out.write('bits  code       (value)  symbol\n')
        for symbol, (bitsize, value) in sorted(self._table.iteritems()):
            out.write('{b:4d}  {c:10} ({v:5d})  {s!r}\n'.format(
                b=bitsize, v=value, s=symbol, c=bin(value)[2:].rjust(bitsize, '0')
            ))

    def encode(self, data):
        """
        Encode given data.

        :param data: sequence of symbols (e.g. byte string, unicode string, list, iterator)
        :return: byte string
        """
        return b''.join(self.encode_streaming(data))

    def encode_streaming(self, data):
        """
        Encode given data in streaming fashion.

        :param data: sequence of symbols (e.g. byte string, unicode string, list, iterator)
        :return: generator of bytes
        """
        # Buffer value and size
        buffer = 0
        size = 0
        for s in itertools.chain(data, [_EOF]):
            b, v = self._table[s]
            # Shift new bits in the buffer
            buffer = (buffer << b) + v
            size += b
            while size >= 8:
                byte = buffer >> (size - 8)
                yield chr(byte)  # TODO py3
                buffer = buffer - (byte << (size - 8))
                size -= 8
        # Final sub-byte chunk
        if size > 0:
            yield chr(buffer << (8 - size))  # TODO py3

    def decode(self, data, as_list=False):
        """
        Decode given data.

        :param data: sequence of bytes (string, list or generator of bytes)
        :param as_list: whether to return as a list instead of
        :return:
        """
        # TODO: autodetect join: as list, as byte string or as unicode string?
        cat = list if as_list else "".join
        return cat(self.decode_streaming(data))

    def decode_streaming(self, data):
        """
        Decode given data in streaming fashion

        :param data: sequence of bytes (string, list or generator of bytes)
        :return: generator of symbols
        """
        # Reverse lookup table: map (bitsize, value) to symbols
        lookup = dict(((b, v), s) for (s, (b, v)) in self._table.iteritems())

        buffer = 0
        size = 0
        for byte in data:
            for m in [128, 64, 32, 16, 8, 4, 2, 1]:
                buffer = (buffer << 1) + bool(ord(byte) & m)
                size += 1
                if (size, buffer) in lookup:
                    symbol = lookup[size, buffer]
                    if symbol == _EOF:
                        return
                    yield symbol
                    buffer = 0
                    size = 0
