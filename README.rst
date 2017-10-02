dahuffman - Python Module for Huffman Encoding and Decoding
===========================================================

dahuffman is a pure Python module for Huffman encoding and decoding,
commonly used for lossless data compression.

The name of the module refers to the full name of the inventor
of the Huffman code tree algorithm: David Albert Huffman (August 9, 1925 – October 7, 1999).

Features and design
-------------------

- Pure Python implementation, only using standard library.
- Leverages iterators and generators internally, allows to be used in streaming fashion.
- Not limited to byte/unicode string input, can handle other "symbols" or tokens,
  for example chess moves or sequences of categorical data, as long as these symbols
  can be used as keys in dictionaries (meaning they should be hashable).

Installation
------------

TODO


Usage
-----

Basic usage example, where the code table is built based on given symbol frequencies::

    >>> from dahuffman import HuffmanCodec
    >>> codec = HuffmanCodec.from_frequencies({'e': 100, 'n':20, 'x':1, 'i': 40, 'q':3})
    >>> encoded = codec.encode('exeneeeexniqneieini')
    >>> encoded
    '\x86|%\x13i@'
    >>> len(encoded)
    6
    >>> codec.decode(encoded)
    'exeneeeexniqneieini'


You can also "train" the codec by providing it data directly::

    >>> codec = HuffmanCodec.from_data('hello world how are you doing today foo bar lorem ipsum')
    >>> codec.encode('do lo er ad od')
    '^O\x1a\xc4S\xab\x80'
    >>> len(_)
    7


Using it with sequences of symbols (country codes in this example)::

    >>> countries = ['FR', 'UK', 'BE', 'IT', 'FR', 'IT', 'GR', 'FR', 'NL', 'BE', 'DE']
    >>> codec = HuffmanCodec.from_data(countries)
    >>> encoded = codec.encode(['FR', 'IT', 'BE', 'FR', 'UK'])
    >>> encoded
    'L\xca'
    >>> len(encoded)
    2
    >>> codec.decode(encoded)
    ['FR', 'IT', 'BE', 'FR', 'UK']



Doing it in a streaming fashion (generators)::

    >>> import random
    >>> def sample(n, symbols):
    ...     for i in range(n):
    ...             if (n-i) % 5 == 1:
    ...                     print(i)
    ...             yield random.choice(symbols)
    ...
    >>> codec = HuffmanCodec.from_data(countries)
    >>> encoded = codec.encode_streaming(sample(16, countries))
    >>> encoded
    <generator object encode_streaming at 0x108bd82d0>
    >>> decoded = codec.decode_streaming(encoded)
    >>> decoded
    <generator object decode_streaming at 0x108bd8370>
    >>> list(decoded)
    0
    5
    10
    15
    ['DE', 'BE', 'FR', 'GR', 'UK', 'BE', 'UK', 'IT', 'UK', 'FR', 'DE', 'IT', 'NL', 'IT', 'FR', 'UK']



