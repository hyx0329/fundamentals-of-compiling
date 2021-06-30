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
        expand = data.get(nt)
        next_set = set()
        for entry in expand:
            for e in entry:
                if e in non_terminal:
                    next_set.add(e)
        prior_graph[nt] = next_set
    return prior_graph


def generate_parents(data: dict):
    """通过孩子记录，求父母"""
    non_terminal = set(data.keys())
    parents = {k: set() for k in data.keys()}
    for k in data.keys:
        for v in data.get(k):
            parents[v].add(k)
    return parents


def prior_sort(parents: dict, initial_item=None):
    non_terminal = set(parents.keys())
    sequence = list()
    current_syms = set()
    empty_set = set()

    # hacky, avoid loop
    if initial_item is not None:
        sequence.append(initial_item)
        current_syms.add(initial_item)
        non_terminal.remove(initial_item)

    while len(non_terminal) > 0:
        new_added = set()
        for sym in non_terminal:
            if current_syms <= parents.get(sym, empty_set):
                sequence.append(sym)
                new_added.add(sym)
        for sym in new_added:
            non_terminal.remove(sym)
        current_syms.update(new_added)
    
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
        for key, v in zip(data.keys(), data.values()):
            for subv in v:
                addition = set()
                before = set([''])
                for k in subv:
                    after = record.get(k, set([k]))
                    if '' in before:
                        addition.update(after)
                    before = after
                if '' in before:
                    addition.add('')
                if record[key] >= addition:
                    continue
                changed_flag = True
                record[key].update(addition)
    return record


def get_follow_set(tables):
    pass


if __name__ == "__main__":
    first_set_test = {
        'S': ['aABe'],
        'A': ['b','Abc'],
        'B': ['d']
    }

    first_set_test_ans = {
        'S': set(['a']),
        'A': set(['b']),
        'B': set(['d']),
    }

    ans = get_first_set(first_set_test)