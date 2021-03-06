from queue import deque
from analyzer.lexer import GrammarLexer


def escaper(data: str):
    """ Escape some characters """
    symbols = ['\\', '+', '*', '?', '(', ')', '&', '|']
    for char in symbols:
        data = data.replace(char, '\\'+char)
    return data


def generate_children(data: dict):
    """求孩子"""
    non_terminal = set(data.keys())
    prior_graph = dict()
    for nt in non_terminal:
        production = data.get(nt)
        next_set = set()
        for entry in production:
            for e in entry:
                if e in non_terminal:
                    next_set.add(e)
        prior_graph[nt] = next_set - set([nt])
    return prior_graph


def generate_parents(data: dict):
    """通过孩子记录，求父母"""
    parents = {k: set() for k in data.keys()}
    for key, value in zip(data.keys(), data.values()):
        for v in value:
            parents[v] = parents.get(v, set())
            parents[v].add(key)
    return parents


def prior_sort(data: dict, initial_item=None):
    """ 根据parents求近似的Topological sorting"""
    children = generate_children(data)
    parents = generate_parents(children)
    non_terminal = set(data.keys())
    read_order = sorted(non_terminal, key=lambda x: len(parents.get(x, set())))
    sequence = list()
    current_syms = set()
    empty_set = set()

    # hacky, just set an initial value
    if initial_item is None:
        initial_item = next(iter(data.keys()))
    sequence.append(initial_item)
    current_syms.add(initial_item)
    read_order.remove(initial_item)

    while len(read_order) > 0:
        new_added = set()
        for sym in read_order:
            pset = parents.get(sym, empty_set)
            if len(current_syms & pset) > 0 or len(pset) == 0:
                sequence.append(sym)
                new_added.add(sym)
        for sym in new_added:
            read_order.remove(sym)
        current_syms.update(new_added)
        # avoid loop stuck
        if len(new_added) == 0:
            sequence.append(read_order[0])
            read_order.pop(0)
    
    return sequence


def loop_detect(children, item):
    child_items = set()
    visit_queue = deque()
    visit_queue.append(item)
    while len(visit_queue) > 0:
        next_item = visit_queue.popleft()
        # TODO: loopdetect


def get_first_set(data, eps_content=''):
    """ 计算first集合
    :param eps_content: 代表"空(epsilon)"内容
    :return: 各个非终结符的first集合
    """
    record = {k: set() for k in data.keys()}
    non_terms = set(data.keys())
    changed_flag = True
    while changed_flag:
        changed_flag = False
        for key, value in zip(data.keys(), data.values()):
            for v in value:
                addition = set()
                before = set([eps_content])
                for k in v:
                    after = record.get(k, set([k]))
                    if eps_content in before:
                        addition.update(after)
                        before = after
                    else:
                        break
                if eps_content in before:
                    addition.add(eps_content)
                if record[key] >= addition:
                    continue
                changed_flag = True
                record[key].update(addition)
    return record


def get_follow_set(data, start=None, eps_content='', end_content='$'):
    """ 生成follow集合
    :param start: 开始状态（有必要，否则随机选取，结果不稳定）
    :param eps_content: 代表"空(epsilon)"内容
    :param end_content: 代表"字符串末尾"的内容
    :return: follow sets, first sets"""
    record = {k: set() for k in data.keys()}
    if start is None:
        start = next(iter(data.keys()))
    record[start].add(end_content)
    eps_set = set([eps_content])
    empty_set = set()
    non_terms = set(data.keys())
    first_record = get_first_set(data, eps_content=eps_content)
    
    for key, value in zip(data.keys(), data.values()):
        for v in value:
            length = len(v)
            if length < 2:
                continue
            for k1, k2 in zip(v[:-1], v[1:]):
                record[k1] = record.get(k1, set()) | first_record.get(k2, set([k2])) - eps_set

    # calculate constraints
    constraints = set()
    for key, value in zip(data.keys(), data.values()):
        for v in value:
            length = len(v)
            if length > 0:
                constraints.add((key, v[-1]))
            for i in range(length-1, 0, -1):
                k1 = v[i]
                k1_set = first_record.get(k1, set([k1]))
                if eps_content in k1_set:
                    k2 = v[i-1]
                    constraints.add((key, k2))
                else:
                    break
    # cleanup constraints
    removing = set()
    for c in constraints:
        if c[0] == c[1]:
            removing.add(c)
        elif c[1] not in non_terms:
            removing.add(c)
    constraints -= removing

    # convert & apply constraints
    converted = {k: set() for k in non_terms}
    for c in constraints:
        converted[c[1]].add(c[0])

    # method 1: bottom-up, feeding parents
    # note: it cannot process constraints with circle(s)
    # WILL STUCK!
    # current_finished = set()
    # while current_finished < non_terms:
    #     for terminal, const in zip(converted.keys(), converted.values()):
    #         if const <= current_finished:
    #             for c in const:
    #                 record[terminal].update(record[c])
    #             current_finished.add(terminal)

    # method 2: closure
    # ensure everyone is fed
    # workaround the circulation
    closure = {k:set() for k in non_terms}
    for c in constraints:
        closure[c[0]].add(c[1])
    for key in closure.keys():
        visit_queue = deque()
        visited = {k: False for k in closure.keys()}
        visit_queue.append(key)
        while len(visit_queue) > 0:
            newkey = visit_queue.popleft()
            visited[newkey] = True
            children = closure[newkey]
            addition = set()
            for k in children:
                if visited[k]:
                    continue
                else:
                    addition.add(k)
                    visit_queue.append(k)
            closure[key].update(addition)
    for key, value in zip(closure.keys(), closure.values()):
        for k in value:
            record[k].update(record[key])

    return record, first_record


def gen_ll_dict(data: list):
    """ 将输入数据转换为字典，分隔符`->`以及`|`"""
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


def transform_grammar(grammar: dict, mapper: GrammarLexer):
    """ 将grammar中的各个元素用mapper转换为记号流
    """
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


def left_factoring(data):
    single = set()
    split_dict = dict()
    for item in data:
        if len(item) == 0:
            single.add(item)
        else:
            split_dict[item[0]] = split_dict.get(item[0], set())
            split_dict[item[0]].add(item[1:])
    to_remove = list()
    for key in split_dict:
        value = split_dict[key]
        if len(value) == 1:
            for v in value:
                single.add(tuple([key]) + v)
                to_remove.append(key)
    for key in to_remove:
        split_dict.pop(key)
    return split_dict, single


if __name__ == "__main__":
    first_set_test = {
        'L': ['E;L', ''],
        'E': ['TG'],
        'G': ['+TG', '-TG', ''],
        'T': ['FH'],
        'H': ['*FH', '/FH', r'%FH', ''],
        'F': ['(E)', 'I', 'N']
    }

    ans = get_follow_set(first_set_test)