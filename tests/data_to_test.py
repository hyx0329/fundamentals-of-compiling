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
        'S': set([]),
        'A': set([]),
        'B': set([])
    }