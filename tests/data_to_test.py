class DataToTest:
    value = {
        '(a|b)*abb': ['abb','abab','abbac','aaabb'],
        '()abc+': ['ab', 'abc', 'abccc'],
        '(a(a|b)*ab)+': ['ab', 'aab', 'abab', 'aaab', 'abbb', 'abbaabbb', 'abbacbb'],
        '(a|b|abc)?abd': ['ab', 'abd', 'aabd', 'babd', 'abcabd', 'abcabcabd']
    }