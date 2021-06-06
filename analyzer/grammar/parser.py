from analyzer.generator.automation import NFA, DFA
from analyzer.generator.matcher import Matcher, BatchMatcher


def _escaper(data: str):
    """ Escape some characters """
    symbols = ['\\', '+', '*', '?', '(', ')', '&', '|']
    for char in symbols:
        data = data.replace(char, '\\'+char)
    return data


class SimpleParser:
    def __init__(self, symbols:list, regexs = None):
        """ 简单的符号流抓换
        
        :param symbols: 单个符号
        :param regexs: 额外的正则(unstable)
        """

        # 符号映射表
        assert isinstance(symbols, list)
        self.mapper = symbols
        for i in symbols:
            assert isinstance(i, str)

        self._regexs = list(map(_escaper, self.mapper))

        if isinstance(regexs, list):
            self._regexs += regexs

        self._matchers = None
        self._batch_matcher = None
        
    def _prepare(self):
        self._matchers = list()
        for rgx in self._regexs:
            nfa = NFA(rgx).compile()
            dfa = DFA(nfa).compile()
            matcher = dfa.minimize().get_matcher()
            self._matchers.append(matcher)
        self._batch_matcher = BatchMatcher(self._matchers)

    def parse(self, data: str):
        """Convert input to a symbol stream
        
        :param data: input string
        :return: a list of symbols
        """
        
        if self._batch_matcher is None:
            self._prepare()
        
        result = self._batch_matcher.consume(data)
        return result


class PredefinedParser(SimpleParser):
    predefined_symbols = (
        [chr(i) for i in range(ord('a'), ord('z')+1)]
        + [chr(i) for i in range(ord('A'), ord('Z')+1)]
        + ['+', '-', '*', '/']
    )

    def __init__(self, extra_symbol = None):
        """ 有默认符号集的解析器
        
        :param extra_symbol: 额外的单词/符号
        """
        symbols = self.predefined_symbols
        if isinstance(extra_symbol, list):
            symbols += extra_symbol
        super().__init__(symbols)
    