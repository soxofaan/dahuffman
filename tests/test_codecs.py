import pytest

from dahuffman import load_json, load_json_compact
from dahuffman.codecs import get_path, load, load_shakespeare, load_shakespeare_lower, load_xml

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
    'json',
    'xml',
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


def test_json():
    codec = load_json()
    data = '{"foo":"bar","baz":[1,2,3,4,5,6],"title":"data stuff"}'
    encoded = codec.encode(data)
    assert codec.decode(encoded) == data


def test_json_compact():
    codec = load_json_compact()
    data = '{"foo":"bar","baz":[1,2,3,4,5,6],"title":"data stuff"}'
    encoded = codec.encode(data)
    assert codec.decode(encoded) == data


def test_xml():
    codec = load_xml()
    data = '<items order="qwux"><item color="red">foo</item></items>'
    encoded = codec.encode(data)
    assert codec.decode(encoded) == data
