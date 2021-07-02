from analyzer.grammar.parser.lr import SLRAutomation
from tests.data_to_test import ParserTestData as test_data_one
from tests.data_to_test_ll import LLTestData as test_data_two
from tests.data_to_test_ll import LLTestDataWithRecursion
from tests.data_to_test_ll import ParserTestData
from tests.utils import print_table


def test_given_example():
    test_set = ParserTestData.raw_set_test
    word_set = ParserTestData.word_set
    test_inputs = ParserTestData.test_inputs
    start_state = ParserTestData.start_state
    
    slr_parser = SLRAutomation(test_set,
                      word_list=word_set,
                      start=start_state)

    mapper = slr_parser.parser.mapper
    assert len(word_set) + 1 == len(mapper)
    mapper_length = len(mapper)

    def map_to_real2(x):
        if isinstance(x, int):
            if x < 0:
                return 'eps'
            elif x < mapper_length:
                return mapper[x]
        return x

    print()
    print('reducable sets')
    for i, item in enumerate(slr_parser.reducable_items):
        print(i, map_to_real2(item[0]), len(item[1]))
    print_table(list(range(len(slr_parser.parsing_table))), slr_parser.pindex, slr_parser.parsing_table, map_to_real2)
    for k, v in zip(slr_parser.grammar.keys(), slr_parser.grammar.values()):
        print(k, v)

    for testin, expect, epos in ParserTestData.test_inputs:
        result, pos = slr_parser.parse(testin)
        # assert pos == epos, pos
        assert result == expect, pos


if __name__ == "__main__":
    test_given_example()
