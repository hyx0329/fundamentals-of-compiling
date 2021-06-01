from .node import Node

"""
控制字符的类别:
    1. 单目
        + 左结合
        + 右结合
    2. 双目
        + 只考虑两边操作数中间控制符
    3. 括号
    4. 隐含字符
    5. 转义符
    6. 其它暂不考虑
    
各种控制的应对策略:
    + 转义符: 进栈等待, 待下一字符直接执行
    + 单目:左结合:不入栈,直接执行
    + 单目:右结合:入栈,等待低/同优先级
    + 双目:入栈,等待低/同优先级
    + 隐含:入栈,等待低/同优先级
    + 左括号:入栈,待匹配
    + 右括号:匹配到左括号
    
对于遇到多个普通字符:
    + 方法1: 提前替换
    + 方法2: 后续判断上一个字符是否是普通字符
"""

ESCAPE_CHAR = '\\'
QUOTES_LEFT = '('
QUOTES_RIGHT = ')'

class StateStorage:
    def __init__(self):
        self.node_list = list()
        self.control_stack = list()
        self.normal_stack = list()
        self.escape_flag = False
        self.last_is_control = True

    def push_control(self, node):
        self.control_stack.append(node)
        return self

    def pop_control(self):
        if self.if_control_empty():
            return None
        else:
            return self.control_stack.pop()

    def top_control(self):
        if (count := len(self.control_stack)) > 0:
            return self.control_stack[count - 1]
        return None

    def push_normal(self, node):
        self.normal_stack.append(node)
        return self

    def pop_normal(self):
        if self.if_normal_empty():
            return None
        else:
            return self.normal_stack.pop()

    def top_normal(self):
        if (count := len(self.control_stack)) > 0:
            return self.control_stack[count - 1]
        return None

    def if_control_empty(self):
        return len(self.control_stack) == 0

    def if_normal_empty(self):
        return len(self.normal_stack) == 0


def do_nothing(*args, **kwargs):
    pass


# 控制符号列表, 按优先级排序
CONTROL_SYMBOLS = (
    (tuple(ESCAPE_CHAR), 1),  # 转义符
    (tuple(QUOTES_RIGHT), 0),  # 括号之类
    (tuple('*+'), 1),  # 单目, 左结合
    # tuple(),  # 单目, 右结合
    (tuple('&'), 2),  # 双目
    (tuple('|'), 2),
    (tuple(QUOTES_LEFT), 0),
    (tuple([None]), 0)  # 以空作为结尾
)


def _compile_symbol_list(symbols):
    level = 0
    compiled = dict()
    for subset in symbols:
        for char in subset[0]:
            compiled[char] = (level, subset[1])  # 优先级, 参数个数
        level += 1
    return compiled


SYMBOL_PROPS = _compile_symbol_list(CONTROL_SYMBOLS)


def process_escape(storage: StateStorage):
    storage.escape_flag = True
    # process


def process_quote(storage: StateStorage):
    control_char = storage.pop_control()
    if control_char in QUOTES_LEFT:
        # 左括号忽略
        return
    else:
        # 右括号, 处理所有的内容直到遇到括号
        last_control = storage.top_control()
        if last_control is None:
                raise ValueError('Extra quote detected!')
        while last_control not in QUOTES_LEFT:
            if SYMBOL_PROPS[last_control][0] <= SYMBOL_PROPS[QUOTES_LEFT[0]][0]:
                handler = function_table[last_control]
                handler(storage)
            last_control = storage.top_control()
            if last_control is None:
                raise ValueError('Extra quote detected!')
        handler = function_table[last_control]
        handler(storage)


def process_closure(storage: StateStorage):
    control_char = storage.pop_control()
    node1: Node = storage.pop_normal()
    node1_section_end: Node = node1.section_end

    warp_right = Node()
    warp_left = Node().set_section_end(warp_right)
    warp_left.join(node1)
    warp_left.join(warp_right)

    node1_section_end.join(warp_right)
    node1_section_end.join(node1)

    storage.push_normal(warp_left)
    storage.node_list.append(warp_left)
    storage.node_list.append(warp_right)


def process_pclosure(storage: StateStorage):
    control_char = storage.pop_control()
    node1: Node = storage.pop_normal()
    node1_section_end: Node = node1.section_end
    warp_right = Node()
    warp_left = Node().set_section_end(warp_right)
    warp_left.join(node1)
    node1_section_end.join(warp_right)
    node1_section_end.join(node1)

    storage.node_list.append(warp_left)
    storage.node_list.append(warp_right)
    storage.push_normal(warp_left)


def process_and(storage: StateStorage):
    control_char = storage.pop_control()
    node2: Node = storage.pop_normal()
    node1: Node = storage.pop_normal()
    node1_end: Node = node1.section_end
    node2_end: Node = node2.section_end

    node1_end.next = node2.next
    node1_end.accept = node2.accept
    node1.set_section_end(node2_end)

    storage.push_normal(node1)
    storage.node_list.remove(node2)


def process_or(storage: StateStorage):
    control_char = storage.pop_control()
    node2 = storage.pop_normal()
    node1 = storage.pop_normal()
    warp_left = Node().join(node1).join(node2)
    warp_right = Node()
    node1.section_end.join(warp_right)
    node2.section_end.join(warp_right)
    warp_left.set_section_end(warp_right)
    storage.push_normal(warp_left)
    storage.node_list.append(warp_left)
    storage.node_list.append(warp_right)


function_table = {
    '\\': process_escape,
    '(': process_quote,
    ')': process_quote,
    '*': process_closure,
    '+': process_pclosure,
    '&': process_and,
    '|': process_or,
    None: do_nothing
}


def control_handler(storage: StateStorage, char):
    # 转义直接进栈
    if storage.escape_flag:
        normal_handler(storage, char)
        storage.escape_flag = False
        storage.last_is_control = False
        return

    if char is not None:
        if char in ESCAPE_CHAR:
            process_escape(storage)
            return

    # 判断之前的符号是否优先执行, 将优先级较高的都处理掉
    last_control = storage.top_control()
    while last_control is not None:
        if SYMBOL_PROPS[last_control][0] > SYMBOL_PROPS[char][0]:
            break
        handler = function_table[last_control]
        handler(storage)
        last_control = storage.top_control()

    # 然后当前控制符进栈等待
    storage.push_control(char)
    storage.last_is_control = True

    # 如果单目, 则先执行
    if SYMBOL_PROPS[char][1] == 1:
        handler = function_table[char]
        handler(storage)
        storage.last_is_control = False


def normal_handler(storage, char):
    if not storage.last_is_control:
        control_handler(storage, '&')
    Node2 = Node()
    Node1 = Node(char).join(Node2).set_section_end(Node2)
    storage.push_normal(Node1)
    storage.node_list.append(Node1)
    storage.node_list.append(Node2)
    storage.last_is_control = False