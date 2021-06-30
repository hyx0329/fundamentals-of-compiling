from analyzer.grammar.parser.utils import *
from .data_to_test import ParserTestData


def test_first_class():
    result = get_first_set(ParserTestData.first_set_test)
    for k in result.keys():
        assert result.get(k) == ParserTestData.first_set_test_ans.get(k), k


def test_follow_class():
    result, _ = get_follow_set(ParserTestData.first_set_test)
    ans = ParserTestData.follow_set_test_ans
    for k in ans.keys():
        assert result.get(k) == ans.get(k), k
    