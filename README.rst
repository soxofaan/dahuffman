dahuffman - Python Module for Huffman Encoding and Decoding
===========================================================


.. image:: https://img.shields.io/github/workflow/status/soxofaan/dahuffman/Lint%20and%20Test
    :target: https://github.com/soxofaan/dahuffman/actions/workflows/lint-and-test.yml

.. image:: https://img.shields.io/badge/license-MIT-blue.svg
    :target: https://github.com/soxofaan/dahuffman/blob/master/LICENSE.txt

.. image::  https://img.shields.io/pypi/v/dahuffman
    :target: https://pypi.org/project/dahuffman

.. image:: https://img.shields.io/pypi/pyversions/dahuffman
    :target: https://pypi.org/project/dahuffman

.. image:: https://img.shields.io/pypi/wheel/dahuffman
    :target: https://pypi.org/project/dahuffman
    :alt: PyPI - Wheel

-------------------------

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
- Properly handle end of encoded bit stream if it does not align with byte boundaries
- For Python 3.5 and up

Installation
------------

.. code-block:: bash

    pip install dahuffman

Usage
-----

Basic usage example, where the code table is built based on given symbol frequencies::

    >>> from dahuffman import HuffmanCodec
    >>> codec = HuffmanCodec.from_frequencies({'e': 100, 'n':20, 'x':1, 'i': 40, 'q':3})
    >>> codec.print_code_table()
    Bits Code  Value Symbol
       5 00000     0 _EOF
       5 00001     1 'x'
       4 0001      1 'q'
       3 001       1 'n'
       2 01        1 'i'
       1 1         1 'e'

Encode a string, get the encoded data as ``bytes`` and decode again::

    >>> encoded = codec.encode('exeneeeexniqneieini')
    >>> encoded
    b'\x86|%\x13i@'
    >>> len(encoded)
    6
    >>> codec.decode(encoded)
    'exeneeeexniqneieini'

If desired: work with byte values directly:

    >>> list(encoded)
    [134, 124, 37, 19, 105, 64]
    >>> codec.decode([134, 124, 37, 19, 105, 64])
    'exeneeeexniqneieini'


You can also "train" the codec by providing it data directly::

    >>> codec = HuffmanCodec.from_data('hello world how are you doing today foo bar lorem ipsum')
    >>> codec.encode('do lo er ad od')
    b'^O\x1a\xc4S\xab\x80'
    >>> len(_)
    7


Using it with sequences of symbols (country codes in this example)::

    >>> countries = ['FR', 'UK', 'BE', 'IT', 'FR', 'IT', 'GR', 'FR', 'NL', 'BE', 'DE']
    >>> codec = HuffmanCodec.from_data(countries)
    >>> encoded = codec.encode(['FR', 'IT', 'BE', 'FR', 'UK'])
    >>> encoded
    b'L\xca'
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




Pre-trained codecs
~~~~~~~~~~~~~~~~~~

The ``dahuffman.codecs`` package contains a bunch of pre-trained code tables.
The codecs can be loaded as follows::

    >>> from dahuffman import load_shakespeare
    >>> codec = load_shakespeare()
    >>> codec.print_code_table()
    Bits Code                     Value Symbol
       4 0000                         0 'n'
       4 0001                         1 's'
       4 0010                         2 'h'
       5 00110                        6 'u'
       7 0011100                     28 'k'
       9 001110100                  116 'Y'
      14 00111010100000            3744 '0'
    ...
    >>> len(codec.encode('To be, or not to be; that is the question;'))
    24
