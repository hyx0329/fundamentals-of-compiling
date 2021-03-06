import pytest
import re

from analyzer.lexer.automation import NFA, DFA
from analyzer.lexer import SimpleLexer
from .data_to_test import RgxTestData as DataToTest

def test_overall():
    data_to_test = DataToTest.value
    for regex, test_data in zip(data_to_test.keys(), data_to_test.values()):
        nfa = NFA(regex)
        nfa.compile()
        dfa = DFA(nfa)
        dfa.minimize()

        re_matcher = re.compile('^{}$'.format(regex))  # add limits

        for tdata in test_data:
            result1, _ = dfa.match(tdata)
            result2 = False if re_matcher.match(tdata) is None else True
            assert result1 == result2, ' '.join((regex, tdata))


def test_simplelexer():
    test_data = None
    