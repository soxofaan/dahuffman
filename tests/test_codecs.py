import pytest

from dahuffman.codecs import get_path, load, load_shakespeare, load_shakespeare_lower

LOREM_IPSUM = '''
    Lorem ipsum dolor sit amet, consectetur adipiscing elit, 
    sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. 
    Dolor sed viverra ipsum nunc aliquet bibendum enim. In massa tempor
    nec feugiat. Nunc aliquet bibendum enim facilisis gravida.
'''


def test_get_path():
    assert get_path('shakespeare') == get_path('shakespeare.pickle')


@pytest.mark.parametrize('name', [
    'shakespeare',
    'shakespeare-lower',
])
def test_encode_decode(name):
    codec = load(name)
    data = LOREM_IPSUM.lower()
    encoded = codec.encode(data)
    assert isinstance(encoded, bytes)
    assert len(encoded) < len(data)
    decoded = codec.decode(encoded)
    assert decoded == data


def test_shakespeare():
    codec = load_shakespeare()
    encoded = codec.encode(LOREM_IPSUM)
    assert codec.decode(encoded) == LOREM_IPSUM


def test_shakespeare_lower():
    codec = load_shakespeare_lower()
    with pytest.raises(KeyError):
        codec.encode(LOREM_IPSUM)
    encoded = codec.encode(LOREM_IPSUM.lower())
    assert codec.decode(encoded) == LOREM_IPSUM.lower()
