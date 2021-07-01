"""
    关于文法：
    + 文法中的每个字符都是有意义的，包括空格
    + 所有非终结符都是BNF/产生式左侧的符号
    + 其它符号都是终结符
"""

from analyzer.lexer import GrammarLexer


def _gen_ll_dict(data: list):
    all_symbols = set()
    nonterm_symbols = set()
    organized = dict()

    # split
    for rule in data:
        non_term, replacements = rule.split('->')
        nonterm_symbols.add(non_term)
        organized[non_term] = replacements.split('|')
    
    # get all symbols(but only for single characters)
    for terms in organized.values():
        for single_term in terms:
            all_symbols.union(single_term)
    
    all_symbols = all_symbols.union(non_term)

    return organized, non_term


def _transform_grammar(grammar: dict, mapper: GrammarLexer):
    transformed_data = dict()
    for k,v in zip(grammar.keys(), grammar.values()):
        # get id for key
        new_k = mapper.parse(k)[0][1]
        # get ids for content
        new_vs = list()
        for entry in v:
            new_entry = mapper.parse(entry)
            new_trans = (i[1] for i in new_entry)  # tuple, for set
            new_vs.append(new_trans)
        transformed_data[new_k] = set(new_vs)  # yeah, set
    return transformed_data


class LLOne:
    def __init__(self, data:list, word_list:list = None, start: str = None, predefined=False):
        # organize grammar data
        organized_data, _ = _gen_ll_dict(data)

        # make a "lexer", so:
        # syms -> nums
        # strings -> tuples
        # -> process human input <-
        if isinstance(word_list, (list, tuple)):
            self.parser = GrammarLexer(word_list, predefined=predefined)
        else:
            self.parser = GrammarLexer(predefined=True)
        
        # thus regenerate all grammar
        self.grammar = _transform_grammar(organized_data, self.parser)
        self.non_terminal_set = list(self.grammar.keys())

        # IDs for newly created non-terminals
        self._extra_non_term_from = len(self.parser.mapper) + 100

        if start is None:
            start = next(iter(self.organized_data.keys()))

        self.start_state = self.parser.mapper.index(start)
        self.first_sets = None
        self.follow_sets = None
        self.parsing_table = None

    def _eliminate_direct_lr(self, non_terminal: int):
        transformed = self.grammar.get(non_terminal, None)
        assert isinstance(transformed, list), "Error non-terminal selection!"

        part_no_recursion = list()
        part_have_recursion = list()
        for entry in transformed:
            if len(entry) == 0:
                break  # cannot process empty substring
            if entry[0] == non_terminal:
                part_have_recursion.append(entry)
            else:
                part_no_recursion.append(entry)
        
        if len(part_have_recursion) > 0:
            new_non_term = self._extra_non_term_from
            self._extra_non_term_from += 1

            for i in range(len(part_have_recursion)):
                original = part_have_recursion[i]
                part_have_recursion[i] = original[1:] + [new_non_term]
            for i in range(len(part_no_recursion)):
                original = part_no_recursion[i]
                part_no_recursion[i] = original + [new_non_term]
            
            part_have_recursion.append([])  # 加一个空
            self.grammar[non_terminal] = part_no_recursion
            self.grammar[new_non_term] = part_have_recursion

    def _eliminate_all_lr(self, grammar: dict, first_nt=None):
        # TODO: implement removing all left recursion
        # ref: https://en.wikipedia.org/wiki/Left_recursion#Removing_direct_left_recursion 
        if first_nt is None:
            first_nt = next(iter(grammar.keys()))
        order = dict()
        all_non_terminals = self.non_terminal_set
        for non_term in all_non_terminals:
            change_flag = True
            while change_flag:
                change_flag = False
                removes = set()
                adds = set()
                for production in self.grammar.get(non_term):
                    if len(production) == 0:
                        continue
                    first_sym = production[0]
                    if first_sym in non_term:
                        removes.add(production)
                        suffix = production[1:]
                        # something
                        
    
    def _gen_parsing_table(self):
        pass

    def parse(self, data: str):
        pass


class LLRewrite:
    def __init__(self):
        self.grammar = None
        self.non_term = set()
        self.characters = set()
    
    def load_grammar(data: list):
        for 

