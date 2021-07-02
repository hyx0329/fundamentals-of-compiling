class ParserTestData:
    word_set = {'E', 'T', 'F', '-', '*', 'id'}
    start_state = 'E'
    raw_set_test = {
        'E->E-T|T',
        'T->T*F|F',
        'F->-F|id'
    }
    test_inputs = {
        ('id-id*id', True, '$'),
        ('id*id-', False, '$')
    }
