from .node import Node
from .control_symbols import *


def _mark_graph(root, number: int ) -> int:
    pass

class NFA:
    def __init__(self, data: str = None):
        self.node_list = None
        self.string_data = data
        self.nfa_table = None
        self.start_node = None
        self.end_node = None

    def compile(self, data: str = None):
        if isinstance(data, str):
            self.string_data = data
        assert isinstance(self.string_data, str), "No data provided!"

        # 准备构建NFA
        state = StateStorage()
        last_char_is_control = True
        current_pos = 0
        data_length = len(self.string_data)

        while current_pos < data_length:

            next_char = self.string_data[current_pos]
            if next_char in SYMBOL_PROPS.keys():
                control_handler(state, next_char)
                last_char_is_control = True if not state.escape_flag else False
            else:
                normal_handler(state, next_char)
                if not last_char_is_control:
                    control_handler(state, '&')
                last_char_is_control = False

            current_pos += 1

        # 收尾操作, 清空栈
        control_handler(state, None)

        # 记录状态
        self.start_node: Node = state.normal_stack.pop()
        self.end_node = self.start_node.section_end
        self.node_list = state.node_list

        # TODO: 转化为表格
        pass

class DFA:
    def __init__(self, nfa_object: NFA):
        self.nfa_object = nfa_object
        self.dfa_table = None
        self.state_set = set()
        self.terminal_set = set()

    def generate(self, nfa_object: NFA):
        pass
