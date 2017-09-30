import dahuffman


def test_basic():
    data = "hello world"
    table = dahuffman.encoding_table(data)
    encoded = dahuffman.encode(table, data)
    decoded = "".join(dahuffman.decode(table, encoded))
    assert decoded == 'hello world'
