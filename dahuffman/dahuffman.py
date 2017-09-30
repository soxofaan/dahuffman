import heapq
from heapq import heappush, heappop, heapify
from collections import defaultdict, Counter
import itertools

# Oneliner to create singleton end-of-file symbol object
_EOF = type('EOF', (object,), {'__repr__': lambda self: '_EOF'})()


def encoding_table(data):
    """
    Build Huffman encoding table from symbol frequency mapping

    @param data: Can be dictionary containing symbol to frequency mapping to convert to encoding table,
        or a sequence of symbols (from which the frequency mapping will be derived).
    @return: mapping of symbol to code tuple (bitsize, value)
    """
    try:
        # Assume `data` is a symbol to frequency mapping
        mapping = data.iteritems()
    except AttributeError:
        # Assume `data` is a symbol sequence
        mapping = Counter(data).iteritems()

    # Heap consists of tuples: (frequency, [list of tuples: (symbol, (bitsize, value))])
    heap = [(f, [(s, (0, 0))]) for s, f in mapping]
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

    # TODO: make table an object supporting human friendly dump, storing to and loading from file, ...
    return dict(heappop(heap)[1])


def encode(table, symbols):
    """
    @param table: mapping of symbol to code tuple (bitsize, value)
    @param symbols: sequence of symbols
    @return generator of bytes as ints
    """
    # TODO make this a method on huffman table?
    # Buffer value and size
    buffer = 0
    size = 0
    for s in itertools.chain(symbols, [_EOF]):
        b, v = table[s]
        # Shift new bits in the buffer
        buffer = (buffer << b) + v
        size += b
        while size >= 8:
            # Time to yield
            byte = buffer >> (size - 8)
            yield byte
            buffer = buffer - (byte << (size - 8))
            size -= 8
    # Final chunk
    if size > 0:
        yield buffer << (8 - size)


def decode(table, code):
    """
    @param table: mapping of symbol to code typle (bitsize, value)
    @param code: sequence of bytes as ints
    @return generator of symbols
    """
    # Inverted (nested) lookup table: map code size to code values to symbols
    # TODO lookup in two levels?
    table = dict(((b, v), s) for (s, (b, v)) in table.iteritems())

    buffer = 0
    size = 0
    for byte in code:
        for m in [128, 64, 32, 16, 8, 4, 2, 1]:
            buffer = (buffer << 1) + bool(byte & m)
            size += 1
            if (size, buffer) in table:
                symbol = table[size, buffer]
                if symbol == _EOF:
                    return
                yield symbol
                buffer = 0
                size = 0
