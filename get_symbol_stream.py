from analyzer.generator.automation import NFA, DFA
from analyzer.generator.matcher import Matcher, MatcherState, BatchMatcher

FUNCTIONS = 'sin|cos|tg|ctg|lg|log|ln'
OPERATORS = '^|\+|-|\*|/|='
SEPARATORS = ' |\t|\n|\\(|\\)|;'
CONSTANTS = 'PI|E'
VARIABLES = '(_|a|b|c|d|e|f|g|h|i|j|k|l|m|n|o|p|q|r|s|t|u|v|w|x|y|z|A|B|C|D|E|F|G|H|I|J|K|L|M|N|O|P|Q|R|S|T|U|V|W|X|Y|Z)(0|1|2|3|4|5|6|7|8|9|a|b|c|d|e|f|g|h|i|j|k|l|m|n|o|p|q|r|s|t|u|v|w|x|y|z|A|B|C|D|E|F|G|H|I|J|K|L|M|N|O|P|Q|R|S|T|U|V|W|X|Y|Z|_)*'
NUMBERS = '((1|2|3|4|5|6|7|8|9)(0|1|2|3|4|5|6|7|8|9)*|0+)(.(0|1|2|3|4|5|6|7|8|9)*(1|2|3|4|5|6|7|8|9))?'

symbols_regex = [
    # 函数
    FUNCTIONS,
    # 运算符
    OPERATORS,
    # 分隔符
    SEPARATORS,
    # 符号常量
    CONSTANTS,
    # 变量名
    VARIABLES,
    # 数字常量
    NUMBERS
]


def _gen_matchers(symbols_regex):
    matchers = list()
    for rgx in symbols_regex:
        nfa = NFA(rgx)
        nfa.compile()
        dfa = DFA(nfa)
        dfa.minimize()
        matchers.append(dfa.get_matcher())
    return matchers


if __name__ == "__main__":
    matchers = _gen_matchers(symbols_regex)
    bmatcher = BatchMatcher(matchers)

    while True:
        bmatcher.reset()
        test_str = input('Input your expression(empty string to exit): ')
        if len(test_str) == 0:
            break
            
        result = bmatcher.consume(test_str)
        for r in result:
            print(r)
    