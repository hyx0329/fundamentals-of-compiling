from .utils import *
from analyzer.lexer import GrammarLexer


def slr_closure(data, grammar):
    """ 状态闭包"""
    items = [tuple(i) for i in data]
    # for each entry in data or ret, format:
    # (non_terminal, production, index_of_point)

    for item in items:
        index = item[2]
        if index < len(item[1]):  # point not at the end
            symbol = item[1][index]
            if symbol in grammar.keys():  # is a non-terminal
                for production in grammar.get(symbol):
                    new_tuple = tuple([symbol, production, 0])  # 
                    if new_tuple not in items:
                        items.append(new_tuple)
    return set(items)  # set


def get_prefix_dfa(grammar, start, symbols):
    """ 获取前缀分析DFA
    :param grammar: 语法
    :param start: 开始状态
    :param symbols: 所有符号(不包括文末记号)
    :return: (items, transisions) DFA状态列表, 状态转移
    """
    # assume already added an extra start state
    ItemsList = list()  # order is REQUIRED, so MUST be a list
    TransitionList = list()  # DFA
    initials = list()
    item_products = grammar.get(start)
    assert len(item_products) == 1
    first_product = next(iter(item_products))  # do not use pop or it'll change the original
    assert len(first_product) == 1

    initials.append(tuple([start, first_product, 0]))
    ItemsList.append(slr_closure(initials, grammar))

    for con_item in ItemsList:
        for sym in symbols:  # for all terminals and non-terminals
            closure = set()
            for item in con_item:
                if item[2] < len(item[1]): # point position not at end
                    if item[1][item[2]] == sym: # same symbol
                        new_tuple = tuple([item[0], item[1], item[2] + 1])
                        closure.add(new_tuple)
    
            new_item = slr_closure(closure, grammar)  # get closure set
    
            if len(new_item) == 0:
                continue

            # either g or s
            action = ''
            if sym in grammar.keys():
                action = 'g'
            else:
                action = 's'
            
            if new_item not in ItemsList:
                ItemsList.append(new_item)

            TransitionList.append(
                tuple([
                    action, 
                    ItemsList.index(con_item),
                    ItemsList.index(new_item),
                    sym
                ])
            )
            
    return ItemsList, TransitionList


def cal_reduce(grammar, start, items_list):
    """ 计算归约
    :param grammar: 语法信息
    :param start: 开始状态
    :param items_list: 自动机状态集
    :return: 接受状态, 归约跳转, 跳转列表"""
    reduce_ = [set() for _ in items_list]
    reducable = list()
    for key, value in zip(grammar.keys(), grammar.values()):
        for v in value:
            new_tuple = tuple([
                key,
                v,
                len(v)
            ])
            reducable.append(new_tuple)

    initial = grammar.get(start)
    assert len(initial) == 1, initial
    init_production = next(iter(initial))  # do not use pop
    assert len(init_production) == 1

    accept = -1

    acc = tuple([start, init_production, 1])
    for state, idx in zip(items_list, range(len(items_list))):
        if acc in state:
            accept = idx
        for item in state:
            if len(item[1]) == item[2]:  # len(production) = position_of_point
                reduce_[idx].add(reducable.index(item))

    return accept, reduce_, reducable


class SLRAutomation:
    def __init__(self, data:set, word_list:(set, tuple, list) = None, start: str = None, predefined=False, end_str_flag='$'):
        """
        :param data:        产生式数据, 多个产生式string
        :param word_list:   单词表, 多个string, 此外空字符不必包含在内
        :param start:       开始状态, 单个string
        :param predefined:  是否使用预置单词表(默认否)
        :param end_string_flag: 在表中标记字符串末尾，默认'$'
        """
        # start state
        real_start_state = '{}\''.format(start)
        old_start_state = start
        word_list = list(word_list)
        word_list.append(real_start_state)
        # argument in advance
        data.add('{}->{}'.format(real_start_state, start))

        # organize grammar data
        organized_data, _ = gen_ll_dict(data)

        # make a "lexer", so:
        # syms -> nums
        # strings -> tuples
        # -> process human input <-
        if isinstance(word_list, (set, list, tuple)):
            self.parser = GrammarLexer(word_list, predefined=predefined)
        else:
            self.parser = GrammarLexer(predefined=True)

        self.start_state = self.parser.mapper.index(real_start_state)


        # thus regenerate all grammar
        self.word_list = word_list
        self.end_str_flag = end_str_flag
        self.grammar = transform_grammar(organized_data, self.parser)
        self.non_terminal_set = list(self.grammar.keys())

        # IDs for newly created non-terminals
        self._extra_non_term_from = len(self.parser.mapper) + 100

        # misc
        self.follow_sets, self.first_sets = get_follow_set(self.grammar, start=self.start_state, eps_content=-1, end_content=self.end_str_flag)
        self._original_state_count = len(self.word_list)
        
        # table index
        # non-terminals
        self.pindex_n = list(self.non_terminal_set)
        # terminals
        self.pindex_t = set(map(lambda x: self.parser.mapper.index(x), self.word_list))
        self.pindex_t.difference_update(self.pindex_n)
        self.pindex_t = list(self.pindex_t)
        self.pindex_t.append(self.end_str_flag)  # add '$' as terminal for convenience
        # combined
        self.pindex = self.pindex_t + self.pindex_n
        self.pindex_rev = {k: v for v,k in enumerate(self.pindex)}

        # table
        self.parsing_table = None
        self.reducable_table = None
        self.reducable_items = None
        self.items_list, self.states_list = get_prefix_dfa(self.grammar, self.start_state, self.pindex_t[:-1] + self.pindex_n)
        self.acc_state = -1
        self._generate_parsing_table()

    def _generate_parsing_table(self):
        accept, reduce_jump, reducable = cal_reduce(self.grammar, self.start_state, self.items_list)
        self.acc_state = accept
        self.reducable_table = reduce_jump
        self.reducable_items = reducable

        all_symbols = self.pindex
        symbol_idxs = self.pindex_rev

        # initialize parsing table
        parsing_table = list()
        for _ in range(len(self.items_list)):
            new_list = [set() for _ in range(len(all_symbols))]
            parsing_table.append(new_list)
        
        # add state transitions
        for item in self.states_list:
            parsing_table[item[1]][symbol_idxs.get(item[3])] \
                .add(tuple([item[0],item[2]]))
        
        # add
        for item, item_idx in zip(reduce_jump, range(len(reduce_jump))):
            if len(item) > 0:  # if not empty
                for idx in item:
                    non_term = reducable[idx][0]
                    follows = self.follow_sets.get(non_term)  # get non terminal
                    for follow in follows:
                        parsing_table[item_idx][symbol_idxs.get(follow)] \
                            .add(tuple(('r', idx)))
        
        parsing_table[accept][symbol_idxs[self.end_str_flag]] = set([tuple(('acc', -1))])
        self.parsing_table = parsing_table

        assert len(self.parsing_table) == len(self.reducable_table), (len(parsing_table), len(reduce_jump))

    def parse(self, data:str):
        """ 尝试匹配"""
        # parsing table and goto table
        parse_t = self.parsing_table
        goto_t = self.reducable_table
        # reducable items
        ritems = self.reducable_items
        # symbol -> id
        symbol_map = self.pindex_rev

        # convert string to a symbol stream, each item consists of the original item and its id
        symbol_list = self.parser.parse(data)
        # then convert to a stack
        input_syms = list(symbol_list)
        input_syms.append(('$', self.end_str_flag))  # end, id is end_str_flag
        input_syms.reverse()
        # setup initial state stack, each item consists of a symbol and a status id
        state_stack = list()
        state_stack.append(('$', 0))  # initial state is zero


        while len(state_stack) > 0 and len(input_syms) > 0:
            state_top = state_stack[-1]
            input_top = input_syms[-1]
            status_id = state_top[1]
            input_sym = input_top[1]

            choices = parse_t[status_id][symbol_map[input_sym]]
            if len(choices) == 0:
                return False, input_top[0]
            
            assert len(choices) == 1, "Parsing failure! Table is not SLR!"

            choice = next(iter(choices))
            action = choice[0]
            param = choice[1]

            if action == 'acc':
                return True, input_top[0]

            elif action == 'r':
                # reduce
                length = len(ritems[param][1])
                if length >= len(state_stack):
                    return False, input_top[0]
                for i in range(length):
                    state_stack.pop()
                current_state = state_stack[-1][1]
                new_sym = ritems[param][0]
                new_state_choices = parse_t[current_state][symbol_map[new_sym]]
                new_state = next(iter(new_state_choices))[1]
                state_stack.append(tuple((new_sym, new_state)))
            elif action == 's':
                # shift
                input_syms.pop()
                state_stack.append(tuple((input_sym, param)))
            else:
                return False, input_top[0]

