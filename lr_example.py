from analyzer.grammar.parser.lr import SLRAutomation
from tests.data_to_test_lr import ParserTestData
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
    rules = set()
    symbols = set()

    i = 1
    while True:
        rule = input('Your rule #{}(stop by empty input):'.format(i))
        if len(rule) == 0:
            break
        i += 1
        rules.add(rule)

    start_state = input('Your initial state:')

    syms = input("Your symbols(seperated by commas):")
    symbols.update(syms.split(','))
    symbols.difference_update(set(['']))
    
    slr_parser = SLRAutomation(rules, symbols, start_state)
    mapper = slr_parser.parser.mapper
    mapper_length = len(mapper)
    parsing_table = slr_parser.parsing_table

    def map_to_real2(x):
        if isinstance(x, int):
            if x < 0:
                return 'eps'
            elif x < mapper_length:
                return mapper[x]
        return x

    print("ID, non-terminal, and correspoding reduce count:")
    for i, var in enumerate(slr_parser.reducable_items):
        print(i, '\t', map_to_real2(var[0]), '\t', len(var[1]))

    print('Parsing table:')
    print_table(
        list(range(len(slr_parser.parsing_table))), 
        slr_parser.pindex,
        slr_parser.parsing_table,
        map_to_real2
    )

    while True:
        string = input("Test string(empty to quit):")
        if len(string) == 0:
            break
        result, sym = slr_parser.parse(string)
        if result:
            print('Good input!')
        else:
            print('Bad input at symbol "{}".'.format(sym))
