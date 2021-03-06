from analyzer.grammar.parser.ll import LLOne
from .data_to_test import ParserTestData as test_data_one
from .data_to_test_ll import LLTestData as test_data_two
from .data_to_test_ll import LLTestDataWithRecursion
from .utils import print_table


def test_ll_no_recursion():
    characters = set('LEGTHFIN;-+*/*()%')
    # characters.add('@')
    ll_parser = LLOne(test_data_one.raw_set_test,
                      word_list=characters,
                      start='L')
    mapper = ll_parser.parser.mapper

    assert len(characters) == len(mapper)
    mapper_length = len(mapper)

    result_first_sets = ll_parser.first_sets
    result_follow_sets = ll_parser.follow_sets

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
    
    # print_table(ll_parser.pindex_n, ll_parser.pindex_t, ll_parser.parsing_table, map_to_real2)
    # for k, v in zip(ll_parser.grammar.keys(), ll_parser.grammar.values()):
    #     print(k, v)


def test_ll_more_complex():
    test_set = test_data_two.raw_set_test
    word_set = test_data_two.word_set
    start_state = test_data_two.start_state
    ll_parser = LLOne(test_set,
                      word_list=word_set,
                      start=start_state)
    mapper = ll_parser.parser.mapper

    assert len(word_set) == len(mapper)
    mapper_length = len(mapper)

    def map_to_real2(x):
        if isinstance(x, int):
            if x < 0:
                return 'eps'
            elif x < mapper_length:
                return mapper[x]
        return x
    
    # print_table(ll_parser.pindex_n, ll_parser.pindex_t, ll_parser.parsing_table, map_to_real2)
    # for k, v in zip(ll_parser.grammar.keys(), ll_parser.grammar.values()):
    #     print(k, v)
    
    for testin, expect in test_data_two.test_inputs:
        result, pos = ll_parser.parse(testin)
        assert result == expect, pos


def test_ll_has_recursion():
    test_set = LLTestDataWithRecursion.raw_set_test
    word_set = LLTestDataWithRecursion.word_set
    test_inputs = LLTestDataWithRecursion.test_inputs
    start_state = LLTestDataWithRecursion.start_state
    
    ll_parser = LLOne(test_set,
                      word_list=word_set,
                      start=start_state)

    for testin, expect, epos in LLTestDataWithRecursion.test_inputs:
        result, pos = ll_parser.parse(testin)
        assert pos == epos, pos
        assert result == expect, pos
