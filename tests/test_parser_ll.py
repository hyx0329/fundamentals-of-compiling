from analyzer.grammar.parser.ll import LLOne
from .data_to_test import ParserTestData as test_data_one
from .data_to_test_ll import LLTestData as test_data_two


def test_ll_no_recursion():
    characters = set('LEGTHFIN;-+*/*()')
    # characters.add('@')
    ll_parser = LLOne(test_data_one.raw_set_test,
                      word_list=characters,
                      start='L')
    print()
    for d in ll_parser.first_sets, ll_parser.follow_sets:
        for k, v in zip(d.keys(), d.values()):
            print(k, v)
        print()
    print()
    print(ll_parser.parser._regexs)