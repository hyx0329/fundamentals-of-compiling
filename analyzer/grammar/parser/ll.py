"""
    关于文法：
    + 文法中的每个字符都是有意义的，包括空格
    + 所有非终结符都是BNF/产生式左侧的符号
    + 其它符号都是终结符
"""

from analyzer.lexer import GrammarLexer
from .utils import get_first_set, get_follow_set, prior_sort


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
            new_trans = tuple(i[1] for i in new_entry)  # tuple, for set
            new_vs.append(new_trans)
        transformed_data[new_k] = set(new_vs)  # yeah, set
    # print()
    # for k,v in zip(transformed_data.keys(), transformed_data.values()):
    #     print(k, v)
    # print()
    return transformed_data


class LLOne:
    """ LL(1) Parser
    使用LL(1)算法，并将所有的输入符号都转化为了数字记号流。

    接受普通字符串形式的产生式，然后将产生式转化为记号流、符号形式
    的文法。请注意，由于使用的dict、set等数据结构，使得符号对应ID
    并不稳定。
    """
    def __init__(self, data:list, word_list:(set, tuple, list) = None, start: str = None, predefined=False, end_str_flag='$'):
        """
        :param data:        产生式数据, 多个产生式string
        :param word_list:   单词表, 多个string, 此外空字符不必包含在内
        :param start:       开始状态, 单个string
        :param predefined:  是否使用预置单词表(默认否)
        :param end_string_flag: 在表中标记字符串末尾，默认'$'
        """
        # organize grammar data
        organized_data, _ = _gen_ll_dict(data)

        # make a "lexer", so:
        # syms -> nums
        # strings -> tuples
        # -> process human input <-
        if isinstance(word_list, (set, list, tuple)):
            self.parser = GrammarLexer(word_list, predefined=predefined)
        else:
            self.parser = GrammarLexer(predefined=True)
        
        # thus regenerate all grammar
        self.word_list = word_list
        self.end_str_flag = end_str_flag
        self.grammar = _transform_grammar(organized_data, self.parser)
        self.non_terminal_set = list(self.grammar.keys())

        # IDs for newly created non-terminals
        self._extra_non_term_from = len(self.parser.mapper) + 100

        # start state
        self.start_state = self.parser.mapper.index(start)
        
        # eliminate left recursion
        self._eliminate_all_lr()

        if start is None:
            start = next(iter(self.organized_data.keys()))

        self.follow_sets, self.first_sets = get_follow_set(self.grammar, start=self.start_state, eps_content=-1, end_content=self.end_str_flag)
        self.parsing_table = None
        self.pindex_n = list(self.non_terminal_set)                     # non-terminals
        self.pindex_t = set(map(lambda x: self.parser.mapper.index(x), self.word_list))
        self.pindex_t.difference_update(self.pindex_n)
        self.pindex_t = list(self.pindex_t)
        self.pindex_t.append(self.end_str_flag)  # terminals
        self._generate_parsing_table()

    def _eliminate_direct_lr(self, non_terminal):
        productions = self.grammar.get(non_terminal, None)
        assert isinstance(productions, set), "Error non-terminal selection!"

        part_no_recursion = set()
        part_have_recursion = set()
        new_non_terminal = self._extra_non_term_from

        for entry in productions:
            if len(entry) == 0:
                break  # cannot process empty substring
            if entry[0] == non_terminal:
                part_have_recursion.add(entry[1:])
            else:
                part_no_recursion.add(entry + tuple([new_non_terminal]))
        
        if len(part_have_recursion) > 0:
            self._extra_non_term_from += 1
            part_have_recursion.add(tuple([-1]))  # 加一个空

            self.grammar[non_terminal] = part_no_recursion
            self.grammar[new_non_term] = part_have_recursion

    def _eliminate_all_lr(self):
        # TODO: implement removing all left recursion
        # ref: https://en.wikipedia.org/wiki/Left_recursion#Removing_direct_left_recursion 
        grammar = self.grammar
        first_nt = self.start_state
        all_non_terminals = self.non_terminal_set
        if first_nt is None:
            first_nt = next(iter(grammar.keys()))
        # temp order
        order = prior_sort(grammar, initial_item=first_nt)

        for non_term in all_non_terminals:
            change_flag = True
            while change_flag:
                change_flag = False
                removes = set()
                adds = set()
                for production in grammar.get(non_term):
                    if len(production) == 0:
                        continue
                    first_sym = production[0]
                    if first_sym in all_non_terminals:
                        if order.index(first_sym) < order.index(non_term):
                            removes.add(production)
                            suffix = production[1:]
                            for rule in grammar.get(first_sym, set()):
                                adds.add(rule+suffix)
                if len(removes) > 0:
                    change_flag = True
                    to_change = self.grammar.get(non_term)
                    to_change.difference_update(removes)
                    to_change.update(adds)
            self._eliminate_direct_lr(non_term)

    def _generate_parsing_table(self):
        firsts = self.first_sets
        follows = self.follow_sets
        parsing_table = list()
        for non_term in self.pindex_n:
            productions = self.grammar.get(non_term)
            row = [None for _ in self.pindex_t]
            follow_set = self.follow_sets.get(non_term)
            for prod in productions:
                firsts = set()
                length = len(prod)
                empty = True
                for p in prod:
                    sub_first = self.first_sets.get(p, set([p]))
                    firsts.update(sub_first)
                    if -1 not in sub_first:
                        empty = False
                        break
                if not empty:
                    firsts.difference_update(set(tuple([-1])))
                else:
                    firsts.add(tuple([-1]))
                for terminal in self.pindex_t:
                    if terminal in firsts:
                        idx = self.pindex_t.index(terminal)
                        row[idx] = prod
                    if tuple([-1]) in firsts:
                        print(follow_set)
                        for t in follow_set:
                            idx = self.pindex_t.index(t)
                            row[idx] = prod
            parsing_table.append(row)
        self.parsing_table = parsing_table

    def parse(self, data: str):
        pass


class LLRewrite:
    def __init__(self):
        self.grammar = None
        self.non_term = set()
        self.characters = set()
    
    def load_grammar(data: list):
        pass

