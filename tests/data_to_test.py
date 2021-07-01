class RgxTestData:
    value = {
        '(a|b)*abb': ['abb','abab','abbac','aaabb'],
        '()abc+': ['ab', 'abc', 'abccc'],
        '(a(a|b)*ab)+': ['ab', 'aab', 'abab', 'aaab', 'abbb', 'abbaabbb', 'abbacbb'],
        '(a|b|abc)?abd': ['ab', 'abd', 'aabd', 'babd', 'abcabd', 'abcabcabd']
    }


class ParserTestData:
    first_set_test = {
        'L': ['E;L', ''],
        'E': ['TG'],
        'G': ['+TG', '-TG', ''],
        'T': ['FH'],
        'H': ['*FH', '/FH', r'%FH', ''],
        'F': ['(E)', 'I', 'N']
    }
    first_set_test_ans = {
        'L': set(['', '(', 'I', 'N']),
        'E': set(['(', 'I', 'N']),
        'G': set(['+', '-', '']),
        'T': set(['(', 'I', 'N']),
        'H': set(['*', '/', '%', '']),
        'F': set(['(', 'I', 'N'])
    }
    follow_set_test_ans = {
        'L': set(['$']),
        'E': set([')', ';']),
        'G': set([')', ';']),
        'T': set(['+', '-', ';', ')']),
        'H': set(['+', '-', ';', ')']),
        'F': set(['+', '-', '*', '/', '%', ')', ';'])
    }
    children_ans = {
        'L': set(['E']),
        'E': set(['T', 'G']),
        'G': set(['T']),
        'T': set(['F', 'H']),
        'H': set(['F']),
        'F': set(['E'])
    }
    parents_ans = {
        'L': set(),
        'E': set(['L', 'F']),
        'G': set(['E']),
        'T': set(['G', 'E']),
        'H': set(['T']),
        'F': set(['T','H'])
    }
    topological_like_order = ('L', 'E', 'G', 'T', 'H', 'F')