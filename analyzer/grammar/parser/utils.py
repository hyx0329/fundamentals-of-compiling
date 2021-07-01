from queue import deque


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


def get_first_set(data):
    record = {k: set() for k in data.keys()}
    non_terms = set(data.keys())
    changed_flag = True
    while changed_flag:
        changed_flag = False
        for key, value in zip(data.keys(), data.values()):
            for v in value:
                addition = set()
                before = set([''])
                for k in v:
                    after = record.get(k, set([k]))
                    if '' in before:
                        addition.update(after)
                        before = after
                    else:
                        break
                if '' in before:
                    addition.add('')
                if record[key] >= addition:
                    continue
                changed_flag = True
                record[key].update(addition)
    return record


def get_follow_set(data, start=None):
    record = {k: set() for k in data.keys()}
    if start is None:
        start = next(iter(data.keys()))
    record[start].add('$')
    eps_set = set([''])
    empty_set = set()
    non_terms = set(data.keys())
    first_record = get_first_set(data)
    
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
                if '' in k1_set:
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