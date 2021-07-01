from analyzer.grammar.parser.ll import LLOne
from .data_to_test import ParserTestData as test_data_one
from .data_to_test_ll import LLTestData as test_data_two


def test_ll_no_recursion():
    characters = set('LEGTHFIN;-+*/*()%')
    # characters.add('@')
    ll_parser = LLOne(test_data_one.raw_set_test,
                      word_list=characters,
                      start='L')
    mapper = ll_parser.parser.mapper

    assert len(characters) == len(mapper)

    result_first_sets = ll_parser.first_sets
    result_follow_sets = ll_parser.follow_sets

    converted_firsts = dict()
    converted_follows = dict()

    def map_to_real(x):
        if isinstance(x, int):
            if x < 0:
                return ''
            else:
                return mapper[x]
        else:
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
    