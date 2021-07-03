# coding=utf-8
from analyzer.grammar.parser.lr import SLRAutomation
from analyzer.lexer import SimpleLexer
from copy import deepcopy

class ArithmeticAnalysis(SLRAutomation):
    grammar = {
        'E->E+T|T',
        'T->T*F|F',
        'F->(E)|-F|id'
    }
    word_list = 'E,T,F,id,(,),*,+,-'.split(',')
    start_nt = 'E'
    regexs = {
        'id': '(1|2|3|4|5|6|7|8|9)(0|1|2|3|4|5|6|7|8|9)*',
        '-': '-',
        '+': '\\+',
        '*': '\\*',
        '(': '\\(',
        ')': '\\)'
    }

    rules = {
        'E+T': ('add', 0, 2, 'new'),
        'T*F': ('times', 0, 2, 'new'),
        '(E)': ('let', 1, -1, 'new'),
        '-F': ('invert', 1, -1, 'new'),
        'id': ('let', 0, -1, 'new'),
        'F': ('let', 0, -1, 'new'),
        'T': ('let', 0, -1, 'new')
    }


    def __init__(self):
        match_regex = list()
        mapping_list = list()
        for key, value in zip(self.regexs.keys(), self.regexs.values()):
            match_regex.append(value)
            mapping_list.append(key)
        
        lexer = SimpleLexer(list(), regexs=match_regex)

        self.lex_map = mapping_list
        self.lexer = lexer

        super().__init__(set(self.grammar), self.word_list, self.start_nt)

    def parse(self, data):
        """
        :param data: 输入字符串
        :return: [bool, list] 状态， 四元式列表"""
        limit = len(self.regexs)
        stream = self.lexer.parse(data)
        for item in stream:
            if item[1] == limit:
                return False, list()
            elif self.lex_map[item[1]] == 'id':
                item[0] = int(item[0])
        
        # convert stream to SLR style
        slr_stream = list()
        for item in stream:
            sym_type = self.lex_map[item[1]]
            sym_type_id = self.parser.mapper.index(sym_type)
            slr_stream.append((item[0], sym_type_id))
        
        ## parse the new stream

        # parsing table and goto table
        parse_t = self.parsing_table
        goto_t = self.reducable_table
        # reducable items
        ritems = self.reducable_items
        # symbol -> id
        symbol_map = self.pindex_rev

        # use another marker
        symbol_list = slr_stream
        # then convert to a stack
        input_syms = list(symbol_list)
        input_syms.append(('$', self.end_str_flag))  # end, id is end_str_flag
        input_syms.reverse()
        # setup initial state stack, each item consists of a symbol and a status id
        state_stack = list()
        state_stack.append(('$', 0))  # initial state is zero

        # three-address code
        code_list = list()
        variable_id = 0

        while len(state_stack) > 0 and len(input_syms) > 0:
            state_top = state_stack[-1]
            input_top = input_syms[-1]
            status_id = state_top[1]
            input_sym = input_top[1]

            choices = parse_t[status_id][symbol_map[input_sym]]
            if len(choices) == 0:
                return False, list()
            
            assert len(choices) == 1, "Parsing failure! Table is not SLR!"

            choice = next(iter(choices))
            action = choice[0]
            param = choice[1]

            if action == 'acc':
                return True, code_list

            elif action == 'r':
                # reduce
                reduce_item = ritems[param][1]
                length = len(reduce_item)
                if length >= len(state_stack):
                    return False, list()
                
                # convert to code
                reduce_item_key = ''.join((self.parser.mapper[i] for i in reduce_item))
                real_words = list()
                for i in range(length):
                    real_word = state_stack.pop()
                    real_word = real_word[0]
                    real_words.append(real_word)
                real_words.reverse()
                code_piece = list(self.rules.get(reduce_item_key))
                assert code_piece is not None
                
                # assign a new id to the new non-terminal
                new_var_id = str(variable_id)
                variable_id += 1

                current_state = state_stack[-1][1]
                new_sym = ritems[param][0]
                new_state_choices = parse_t[current_state][symbol_map[new_sym]]
                new_state = next(iter(new_state_choices))[1]

                # push back new state
                state_stack.append(tuple((new_var_id, new_state)))

                # generate new code
                for i in range(1, 3):
                    idx = code_piece[i]
                    if idx < 0:
                        continue
                    code_piece[i] = real_words[idx]
                code_piece[3] = new_var_id
                code_list.append(code_piece)

            elif action == 's':
                # shift
                input_syms.pop()
                state_stack.append(tuple((input_top[0], param)))
            else:
                return False, list()

    def run_code(self, data):
        """ 执行四元式，注意这里没有拓扑排序"""
        variable_table = dict()
        for entry in data:
            action = entry[0]
            param1 = variable_table[entry[1]] if isinstance(entry[1], str) else entry[1]
            param2 = variable_table[entry[2]] if isinstance(entry[2], str) else entry[2]
            param3 = entry[3]

            if action == 'let':
                variable_table[param3] = param1
            elif action == 'add':
                variable_table[param3] = param1 + param2
            elif action == 'times':
                variable_table[param3] = param1 * param2
            elif action == 'invert':
                variable_table[param3] = -param1
            else:
                raise ValueError("Unexpected action:", action)
        
        return variable_table[param3], variable_table
