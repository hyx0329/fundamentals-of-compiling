from .node import Node
from .control_symbols import *

from collections import deque


def _mark_graph(root: Node, number: int) -> int:
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

        # 编号
        _mark_graph(self.start_node, 0)
        # 排序
        self.node_list = sorted(self.node_list, key=lambda x: x.id)

        # TODO: 改善表格结构
        self.nfa_table = list()
        for sub_node in self.node_list:
            next_ids = list()
            if isinstance(sub_node.next, list):
                # if len(sub_node.next) == 0:  # 终点
                #     next_ids.append('ACC')
                for next_node in sub_node.next:
                    next_ids.append(next_node.id)
            self.nfa_table.append(next_ids)
        pass


def _gen_closure(node_id: int, nfa_accept_list: (list, tuple), nfa_jump_table: (list, tuple), accept=None):
    """
    计算单个节点跳转闭包

    :param node_id: 起始节点编号
    :param nfa_accept_list: 各个节点接受字符列表
    :param nfa_jump_table: 跳转列表
    :param accept: 目标接受符
    :return: 所求闭包集合
    """
    node_queue = deque()
    node_queue.append(node_id)
    closure = set()
    end_flag = False
    while len(node_queue) > 0:
        next_node_id = node_queue.popleft()
        if next_node_id in closure:
            # 此时遍历过，不再重复操作
            continue
        else:
            closure.add(next_node_id)
            # 添加新的候选节点
            if nfa_accept_list[next_node_id] is None:
                for nid in nfa_jump_table[next_node_id]:
                    node_queue.append(nid)
    return closure


def _gen_closure_from_set(id_set, nfa_accept_list, nfa_jump_table, accept=None):
    all_closure = set()
    for nodei in id_set:
        all_closure = all_closure.union(
            _gen_closure(nodei, nfa_accept_list, nfa_jump_table, accept=accept)
            )
    return all_closure


def _get_next_state(state_set, accept, nfa_accept_list, nfa_jump_table):
    all_next_state = set()
    for substate in state_set:
        new_next_states = set()
        if nfa_accept_list[substate] == accept:
            all_next_state = all_next_state.union(nfa_jump_table[substate])
    return all_next_state


class DFA:
    def __init__(self, nfa_object: NFA = None):
        self.nfa_object = nfa_object
        self.dfa_table = list()
        self.terminal_set = set()
        self.character_set = None

    def compile(self, nfa_object: NFA = None):
        if nfa_object is not None:
            self.nfa_object = nfa_object

        assert isinstance(self.nfa_object, NFA), "No valid data provided!"

        nfa_accept_list = [node.accept for node in self.nfa_object.node_list]
        nfa_jump_table = self.nfa_object.nfa_table

        character_set = set(nfa_accept_list)
        if None in character_set:
            character_set.remove(None)
        terminal_state = len(nfa_jump_table) - 1

        initial_state_set = _gen_closure(0, nfa_accept_list, nfa_jump_table)

        dstates_list = list()
        dstates_props = list()
        dstates_queue = deque()

        dstates_list.append(initial_state_set)
        dstates_queue.append(initial_state_set)

        while len(dstates_queue) > 0:
            new_dstate = dstates_queue.popleft()
            jump_table = dict()
            for char in character_set:
                next_state = _get_next_state(new_dstate, char, nfa_accept_list, nfa_jump_table)
                next_state_closure = _gen_closure_from_set(next_state, nfa_accept_list, nfa_jump_table)
                if len(next_state_closure) == 0:
                    state_id = None
                else:
                    try:
                        state_id = dstates_list.index(next_state_closure)
                    except ValueError:
                        state_id = len(dstates_list)
                        dstates_list.append(next_state_closure)
                        dstates_queue.append(next_state_closure)
                jump_table[char] = state_id
            # 标记终态
            if terminal_state in new_dstate:
                terminal_flag = True
            else:
                terminal_flag = False
            dstates_props.append((jump_table, terminal_flag))

        self.character_set = list(character_set)
        self.dfa_table = list()
        # 构建表格形式的跳转表
        for prop in dstates_props:
            jump_entry = list()
            for char in self.character_set:
                jump_target = prop[0].get(char, None)
                jump_entry.append(jump_target)
            self.dfa_table.append(jump_entry)
        # 记录一下终节点
        for i in range(len(dstates_props)):
            if dstates_props[i][1] == True:
                self.terminal_set.add(i)
    
    def minimize(self):
        pass