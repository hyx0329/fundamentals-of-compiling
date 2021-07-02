from analyzer.grammar.parser.lr import SLRAutomation
from .data_to_test import ParserTestData as test_data_one
from .data_to_test_ll import LLTestData as test_data_two
from .data_to_test_ll import LLTestDataWithRecursion
from .data_to_test_lr import ParserTestData
from .utils import print_table
import pytest


# @pytest.mark.skip(reason="skip")
def test_slr_working_with_first_follow():
    characters = set('LEGTHFIN;-+*/*()%')
    # characters.add('@')
    slr_parser = SLRAutomation(test_data_one.raw_set_test,
                      word_list=characters,
                      start='L')
    mapper = slr_parser.parser.mapper

    assert len(characters) + 1 == len(mapper)
    mapper_length = len(mapper)

    result_first_sets = slr_parser.first_sets
    result_follow_sets = slr_parser.follow_sets

    converted_firsts = dict()
    converted_follows = dict()

    def map_to_real(x):
        if isinstance(x, int):
            if x < 0:
                return ''
            elif x < mapper_length:
                return mapper[x]
        return x
    
    def map_to_real2(x):
        if isinstance(x, int):
            if x < 0:
                return 'eps'
            elif x < mapper_length:
                return mapper[x]
        return x
    
    pairs = (
        (result_first_sets, converted_firsts),
        (result_follow_sets, converted_follows)
    )

    for source, target in pairs:
        for key, value in zip(source.keys(), source.values()):
            converted_value = set(map(map_to_real, value))
            ckey = mapper[key]
            target[ckey] = converted_value
    
    test_pairs = (
        (converted_firsts, test_data_one.first_set_test_ans),
        (converted_follows, test_data_one.follow_set_test_ans)
    )
    for ret, ans in test_pairs:
        for key in ans.keys():
            assert ret.get(key) == ans.get(key), key
        assert ret.get('L\'') == ans.get('L'), key


@pytest.mark.skip(reason="SLR cannot deal with epsilon")
def test_slr_more_complex():
    test_set = test_data_two.raw_set_test
    word_set = test_data_two.word_set
    start_state = test_data_two.start_state
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
    
    # print()
    # print('reducable sets')
    # for i, item in enumerate(slr_parser.reducable_items):
    #     print(i, map_to_real2(item[0]), len(item[1]))
    # print_table(list(range(len(slr_parser.parsing_table))), slr_parser.pindex, slr_parser.parsing_table, map_to_real2)
    # for k, v in zip(slr_parser.grammar.keys(), slr_parser.grammar.values()):
    #     print(k, v)
    
    for testin, expect in test_data_two.test_inputs:
        result, pos = slr_parser.parse(testin)
        assert result == expect, pos


@pytest.mark.skip(reason="SLR cannot deal with epsilon")
def test_slr_has_recursion():
    test_set = LLTestDataWithRecursion.raw_set_test
    word_set = LLTestDataWithRecursion.word_set
    test_inputs = LLTestDataWithRecursion.test_inputs
    start_state = LLTestDataWithRecursion.start_state
    
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

    # print()
    # print('reducable sets')
    # for i, item in enumerate(slr_parser.reducable_items):
    #     print(i, map_to_real2(item[0]), len(item[1]))
    # print_table(list(range(len(slr_parser.parsing_table))), slr_parser.pindex, slr_parser.parsing_table, map_to_real2)
    # for k, v in zip(slr_parser.grammar.keys(), slr_parser.grammar.values()):
    #     print(k, v)
    
    for testin, expect in test_data_two.test_inputs:
        result, pos = slr_parser.parse(testin)
        assert result == expect, pos

    for testin, expect, epos in LLTestDataWithRecursion.test_inputs:
        result, pos = slr_parser.parse(testin)
        assert pos == epos, pos
        assert result == expect, pos


def test_slr_given_example1():
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
    
    # print()
    # print('reducable sets')
    # for i, item in enumerate(slr_parser.reducable_items):
    #     print(i, map_to_real2(item[0]), len(item[1]))
    # print_table(list(range(len(slr_parser.parsing_table))), slr_parser.pindex, slr_parser.parsing_table, map_to_real2)
    # print('acc:', slr_parser.acc_state)
    # for k, v in zip(slr_parser.grammar.keys(), slr_parser.grammar.values()):
    #     print(k, v)

    for testin, expect, epos in ParserTestData.test_inputs:
        result, pos = slr_parser.parse(testin)
        assert pos == epos, pos
        assert result == expect, pos
    