from tbk.utils.graphics import str_table

def test_str_table() -> None:
    data = [
        ['Name (Long)', 'Value (Also Long)'],
        ['hi', 1],
        ['bye', None]
    ]
    output = """
Name (Long) | Value (Also Long)
------------+------------------
hi          | 1
------------+------------------
bye         | None
""".strip('\n')
    assert str_table(data) == output
    output = """
Name (Long) | Value (Also Long)
------------+------------------
         hi |         1
------------+------------------
        bye |        None
""".strip('\n')
    assert str_table(data, [1, 0]) == output
