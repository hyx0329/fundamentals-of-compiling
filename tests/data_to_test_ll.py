class LLTestData:
    start_state = 'L'
    word_set = set('LETF;-+*/() ')
    word_set.add('mod')
    word_set.add('E\'')
    word_set.add('T\'')
    word_set.add('id')
    word_set.add('num')
    raw_set_test = {
        'L->E;L|',
        'E->TE\'',
        'E\'->+TE\'|-TE\'|',
        'T->FT\'',
        'T\'->*FT\'|/FT\'| mod FT\'|',
        'F->(E)|id|num'
    }
    test_inputs = (
        ('id+id+id;', True),
        ('id-id*id;', True),
        ('id+id-', False),
        ('id+id mod id;', True)
    )


class LLTestDataWithRecursion:
    raw_set_test = {
        "L->E;L|",
        "E->E+T|E-T|T",
        "T->T*F|T/F|T mod F|F",
        "F->(E)|id|num"
    }
    start_state = 'L'
    word_set = set('LETF;-+*/() ')
    word_set.add('mod')
    word_set.add('id')
    word_set.add('num')

    test_inputs = (
        ('id+id-id;', True, '$'),
        ('id-id*id;', True, '$'),
        ('id+id-', False, '$'),
        ('id+id-;', False, ';'),
        ('id+id mod id;', True, '$')
    )
