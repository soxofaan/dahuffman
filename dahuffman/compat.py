"""
Poor man's py2/py3 compatibility layer.
"""

import sys

# The handling of byte strings is slightly different between
# Python 2 (str object) and Python 3 (bytes object).
# Encoding from symbols to bytes (and vice versa) is done in a
# correspondingly different way.
if sys.version[0] == '2':
    # Python 2: iterating over a (byte) string yields single characters strings.
    # During encoding and decoding where we work with int values
    # we have to convert explicitly between single character strings and ints.
    to_byte = chr
    from_byte = ord
    concat_bytes = "".join
else:
    # Python 3: iterating over a bytes object yields integers natively,
    # so no conversion necessary.
    to_byte = lambda x: x
    from_byte = lambda x: x
    concat_bytes = bytes

