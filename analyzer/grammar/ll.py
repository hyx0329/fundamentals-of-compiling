"""
    关于文法：
    + 文法中的每个字符都是有意义的，包括空格
    + 所有非终结符都是BNF/产生式左侧的符号
    + 其它符号都是终结符
"""

from .parser import PredefinedParser


def _gen_ll_dict(data: list):
    all_symbols = set()
    nonterm_symbols = set()
    organized = dict()

    for rule in data:
        non_term, replacements = rule.split('->')
        nonterm_symbols.add(non_term)
        organized[non_term] = replacements.split('|')
    for terms in organized.values():
        for single_term in terms:
            all_symbols.union(single_term)
    
    all_symbols = all_symbols.union(non_term)

    return organized, non_term


def _transform_grammar(grammar: dict, mapper: PredefinedParser):
    transformed_data = dict()
    for k,v in zip(grammar.keys(), grammar.values()):
        new_k = mapper.parse(k)[0][1]
        new_vs = list()
        for entry in v:
            new_entry = mapper.parse(entry)
            new_trans = [i[1] for i in new_entry]
            new_vs.append(new_trans)
        transformed_data[new_k] = new_vs
    return transformed_data


class LL:
    def __init__(self, data:list, word_list:list = None, start: str = None):

        organized_data, _ = _gen_ll_dict(data)

        if isinstance(word_list, (list, tuple)):
            self.parser = PredefinedParser(word_list)
        else:
            self.parser = PredefinedParser()
        
        self.grammar = _transform_grammar(organized_data, self.parser)
        self.non_terminal_set = list(self.grammar.keys())

        # 准备新非终结符开始的ID, 供消除左递归时使用
        self._extra_non_term_from = len(self.parser.mapper) + 100

        if start is None:
            start = next(iter(self.organized_data.keys()))

        self.start_state = self.parser.mapper.index(start)
        self.first_set = None
        self.follow_set = None
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

    def _eliminate_all_lr(self, grammar: dict):
        # TODO: implement removing all left recursion
        # ref: https://en.wikipedia.org/wiki/Left_recursion#Removing_direct_left_recursion 
        all_non_terminals = self.non_terminal_set
        for non_term in all_non_terminals:
            change_flag = True
            while change_flag:
                change_flag = False
                for rule in self.grammar.get(non_term):
                    pass
    
    def _gen_first_set(self):
        first_set = dict()
        for key, value in zip(self.grammar.keys(), self.grammar.values()):
            firsts = set()
            for v in value:
                if len(v) > 0:
                    firsts.add(v[0])
                else:
                    firsts.add(None)
            first_set[key] = firsts
        
        self.first_set = first_set

    def _gen_follow_set(self):
        if self.first_set is None:
            self._gen_first_set()
        
        follow_set = dict()
        for key in zip(self.grammar.keys()):
            follow_set[key] = set()
        
        for value in zip(self.grammar.values):
            follows = set()
            for v in value:
                if len(v) < 2:
                    continue

                p1 = v[0]
                p2 = v[1]
                if p1 in self.grammar.keys() and p2 in self.grammar.keys():
                    # TODO: add follow rule 1
                    pass

        for key, value in zip(self.grammar.keys(), self.grammar.values()):
            follows = list()
            for v in value:
                if len(v) > 1:
                    # TODO: add follow rule 2
                    pass
            follow_set[key] = follows

    def _gen_parsing_table(self):
        pass

    def parse(self, data: str):
        pass