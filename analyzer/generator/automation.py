from .node import Node
from .control_symbols import *

from collections import deque

def _mark_graph(root: Node, number: int ) -> int:
    node_queue = deque()
    node_queue.append(root)

    while len(node_queue) > 0:
        next_node: Node = node_queue.popleft()
        if next_node.id is None:
            next_node.id = number
            number += 1
            if isinstance(next_node.next, list):
                for sub_node in next_node.next:
                    node_queue.append(sub_node)
    return number

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
        state.last_is_control = True
        current_pos = 0
        data_length = len(self.string_data)
        try:
            while current_pos < data_length:

                next_char = self.string_data[current_pos]

                # 对于控制字符
                if next_char in SYMBOL_PROPS.keys():
                    state.last_is_control = True if not state.escape_flag else False
                    control_handler(state, next_char)
                # 对于一般字符
                else:
                    if not state.last_is_control:
                        control_handler(state, '&')
                    normal_handler(state, next_char)
                    state.last_is_control = False
                current_pos += 1
            # 收尾操作, 清空栈
            control_handler(state, None)
        except:
            raise ValueError('Error occured at position {}'.format(current_pos))

        # 记录状态
        self.start_node: Node = state.normal_stack.pop()
        self.end_node = self.start_node.section_end
        self.node_list = state.node_list

        # TODO: 转化为表格
        _mark_graph(self.start_node, 0)

        self.node_list = sorted(self.node_list, key=lambda x: x.id)
        self.nfa_table = list()
        for sub_node in self.node_list:
            next_ids = list()
            if isinstance(sub_node.next, list):
                for next_node in sub_node.next:
                    next_ids.append(next_node.id)
            self.nfa_table.append(next_node)
        pass

class DFA:
    def __init__(self, nfa_object: NFA):
        self.nfa_object = nfa_object
        self.dfa_table = None
        self.state_set = set()
        self.terminal_set = set()

    def generate(self, nfa_object: NFA):
        pass
