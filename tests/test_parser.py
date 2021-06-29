from analyzer.lexer.parser import PredefinedParser

def test_parser():
    parser = PredefinedParser()
    result = parser.parse('abcde')
    for r,i in zip(result, range(5)):
        assert r[1] == i, "Code mismatch {},{}".format(r[1], i)

def test_parser_extra_symbol():
    parser = PredefinedParser(['id'])

    table = parser.mapper
    assert len(set(table)) == len(table), "Mapper contains duplicate items"

    result = parser.parse('id+id*id')
    assert len(result) == 5, "Result len mismatch {},{}".format(len(result), 5)

    for r in result:
        cid = r[1]
        symbol = r[0]
        cid_expected = table.index(symbol)
        assert cid == cid_expected, "Unexpected symbol id for '{}'".format(symbol)

def test_parser_empty_data():
    parser = PredefinedParser()
    result = parser.parse('')

    assert result[0][0] == '', "Data mismatch!"
    assert result[0][1] == -1, "Code mismatch!"
