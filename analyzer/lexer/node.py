class Node:
    def __init__(self, accept_char: str = None):
        self.id = None
        self.accept = accept_char
        self.next = list()
        self.section_end = None

    def __repr__(self):
        if self.accept is None:
            return 'None'
        return self.accept

    def set_id(self, node_id):
        self.id = node_id
        return self

    def set_accept(self, accept):
        self.accept = accept
        return self

    def set_section_end(self, node_end):
        self.section_end = node_end
        return self

    def join(self, next_node, clear: bool = False):
        if clear:
            self.next.clear()
        assert len(self.next) <= 2, "the list of next is full"
        self.next.append(next_node)
        # self.section_end = next_node.section_end
        return self


class NodeBox:
    def __init__(self, node: Node = None):
        self.value = node


class NodeGroup:
    def __init__(self):
        self.node_list = list()
        self.head = None
        self.tail = None
