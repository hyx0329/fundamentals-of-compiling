from analyzer.grammar.parser.utils import *
from .data_to_test import ParserTestData


def test_first_class():
    result = get_first_set(ParserTestData.first_set_test)
    for k in result.keys():
        assert result.get(k) == ParserTestData.first_set_test_ans.get(k), result
    