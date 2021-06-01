from .node import Node
from .control_symbols import *

from collections import deque
from itertools import groupby


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
        """
        节点存储跳转条件及目标，所有节点均存放在节点列表中
        nfa_table记录了各个节点的下一跳
        start_node是开始节点, end_node是终止节点
        node_list最后会排序
        """
        self.node_list = None
        self.string_data = data
        self.nfa_table = None
        self.start_node = None
        self.end_node = None
    
    def print_table(self):
        if self.nfa_table is None:
            self.compile()
        
        character_set = list(set([node.accept for node in self.node_list]))

        def _convert_str(data):
            if data is None:
                return "None"
            else:
                return str(data)

        # 表头
        format_string = '{:>8}|'
        separator_string = '{:=>8}|'
        # 分割线
        print('\n|'+separator_string.format(''), end='')
        for _ in range(len(character_set)):
            print(separator_string.format(''), end='')
        print()
        # 表头内容
        print('|'+format_string.format(''), end='')
        for char in character_set:
            print(format_string.format(_convert_str(char)), end='')
        print('\n|'+separator_string.format(''), end='')
        # 分割线
        for _ in range(len(character_set)):
            print(separator_string.format(''), end='')
        print()
        
        # 表格内容
        for state in range(len(self.nfa_table)):
            print('|', end='')
            print(format_string.format(state), end='')
            for char in character_set:
                if self.node_list[state].accept == char:
                    state_string = ','.join(map(str, self.nfa_table[state]))
                    print(format_string.format(state_string), end='')
                else:
                    print(format_string.format(''), end='')
            print()
        # 分割线
        print('|'+separator_string.format(''), end='')
        for _ in range(len(character_set)):
            print(separator_string.format(''), end='')
        print()

    def compile(self, data: str = None):
        if isinstance(data, str):
            self.string_data = data
        assert isinstance(self.string_data, str), "No data provided!"

        # 准备构建NFA
        state = StateStorage()
        # state.last_is_control = True
        current_pos = 0
        data_length = len(self.string_data)
        try:
            while current_pos < data_length:

                next_char = self.string_data[current_pos]

                # 对于控制字符
                if next_char in SYMBOL_PROPS.keys():
                    # state.last_is_control = True if not state.escape_flag else False
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
        except Exception as e:
            raise ValueError('Error occured at position {}, {}'.format(current_pos, e.args[0]))

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
        self.start_id = 0
        self.terminal_set = set()
        self.character_set = None  # list, 字符表
        self.state_set = None

    def print_table(self):
        if self.character_set is None:
            self.compile
        
        # 表头
        format_string = '{:>8}|'
        separator_string = '{:=>8}|'
        character_set = self.character_set
        # 分割线
        print('\n|'+separator_string.format(''), end='')
        for _ in range(len(character_set)):
            print(separator_string.format(''), end='')
        # 表头内容
        print('\n|'+format_string.format(''), end='')
        for char in character_set:
            print(format_string.format(char), end='')
        print('\n|'+separator_string.format(''), end='')
        # 分割线
        for _ in range(len(character_set)):
            print(separator_string.format(''), end='')
        print()
        
        # 表格内容
        for state in range(len(self.dfa_table)):
            print('|', end='')
            print(format_string.format(state), end='')
            for next_state in self.dfa_table[state]:
                print(format_string.format(str(next_state)), end='')
            print()
        # 分割线
        print('|'+separator_string.format(''), end='')
        for _ in range(len(character_set)):
            print(separator_string.format(''), end='')
        print()
        

    def compile(self, nfa_object: NFA = None):
        if nfa_object is not None:
            self.nfa_object = nfa_object

        assert isinstance(self.nfa_object, NFA), "No valid data provided!"

        nfa_accept_list = [node.accept for node in self.nfa_object.node_list]
        nfa_jump_table = self.nfa_object.nfa_table

        character_set = set(nfa_accept_list)
        if None in character_set:
            character_set.remove(None)
        
        terminal_state = self.nfa_object.end_node.id

        initial_state_set = _gen_closure(0, nfa_accept_list, nfa_jump_table)

        dstates_list = list()
        dstates_props = list()
        dstates_queue = deque()

        dstates_list.append(initial_state_set)
        dstates_queue.append(initial_state_set)

        # 开始不断寻找新的空闭包, 找到新的就加入队列
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
        # 记录一下所有节点，尽管没必要
        self.state_set = set([i for i in range(len(self.dfa_table))])
    
    def minimize(self):
        if self.state_set is None:
            self.compile()
        
        # 计算分区    
        partition = [
                    self.state_set - self.terminal_set,
                    self.terminal_set
                ]
        part_queue = deque()
        for part in partition:
            part_queue.append(part)
        
        # 开始分裂
        while len(part_queue) > 0:
            part = part_queue.popleft()
            state_to_group_id = dict()
            # 检测各个状态下接受各个字符后的下一组
            for state in part:
                state_to_group_id[state] = list()
                for jump in self.dfa_table[state]:
                    for i in range(len(partition)):
                        if jump in partition[i]:
                            state_to_group_id[state].append(i)
                            break
            # 合并完全相同的组
            groups = sorted(list(state_to_group_id.values()))
            groups = [ k for k,_ in groupby(groups)]

            # 如果结果只有一个组，则继续
            if len(groups) == 1:
                continue

            # 否则将新生成的组加入队列，并修改原来的分区列表
            new_subgroups = list()
            for g in groups:
                subgroup = set()
                for state, v in zip(state_to_group_id.keys(), state_to_group_id.values()):
                    if v == g:
                        subgroup.add(state)
                new_subgroups.append(subgroup)
            partition.remove(part)
            for p in new_subgroups:
                partition.append(p)
                part_queue.append(p)

        # 分区完毕，进行转换，重映射
        # 排个序好看，另外元组自己会升序排序
        new_state_lists = sorted([list(s) for s in partition])
        new_state_sets = [set(s) for s in new_state_lists]
        new_terminal_set = set()
        new_start_id = 0
        for i in range(len(new_state_sets)):
            if not self.terminal_set.isdisjoint(new_state_sets[i]):
                new_terminal_set.add(i)
            elif self.start_id in new_state_sets[i]:
                new_start_id = i
        
        # 构建新的跳转表
        set_to_set_id = list()
        # 检测各个状态下接受各个字符后的下一组
        for state_set in new_state_sets:
            state = next(iter(state_set))  # 取一个原状态
            state_new_jump = list()
            for jump in self.dfa_table[state]:
                for i in range(len(new_state_sets)):
                    if jump in new_state_sets[i]:
                        state_new_jump.append(i)
                        break
            set_to_set_id.append(state_new_jump)

        # 存储与更新结果
        self.dfa_table = set_to_set_id
        self.terminal_set = new_terminal_set
        self.start_id = new_start_id
        self.state_set = set([i for i in range(len(set_to_set_id))])

    def match(self, test_str: str = ''):
        """
        :param test_str: 输入待检测字符串
        """
        if not isinstance(test_str, str):
            raise ValueError("Unexpected data type '{}'".format(type(test_str)))

        if_match = False

        # 依次读取，状态跳转
        current_pos = 0
        string_length = len(test_str)
        current_state = self.start_id
        while current_pos < string_length:
            current_char = test_str[current_pos]
            try:
                char_id = self.character_set.index(current_char)
            except ValueError:
                raise ValueError("Unexpected character", current_char, current_pos)
                # if_match = False
                # break
            current_state = self.dfa_table[current_state][char_id]
            if current_state is None:
                raise ValueError("Unmatched character", current_char, current_pos)
            current_pos += 1
        
        # 读完，再判断终止状态
        if current_pos == string_length:
            if current_state in self.terminal_set:
                if_match = True

        return if_match
            