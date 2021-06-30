class RgxTestData:
    value = {
        '(a|b)*abb': ['abb','abab','abbac','aaabb'],
        '()abc+': ['ab', 'abc', 'abccc'],
        '(a(a|b)*ab)+': ['ab', 'aab', 'abab', 'aaab', 'abbb', 'abbaabbb', 'abbacbb'],
        '(a|b|abc)?abd': ['ab', 'abd', 'aabd', 'babd', 'abcabd', 'abcabcabd']
    }


class ParserTestData:
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