from analyzer.generator.automation import NFA, DFA

example1 = '(a|b)*bb'

if __name__ == '__main__':
    menu = """
    1. Input Regex (Current: '{}')
    2. Test string
    3. Print NFA matrix
    4. Print DFA matrix
    5. Minimize DFA
    0. Quit
    """

    available_choices = {str(i) for i in range(6)}

    regex_str = ''
    nfa_obj = None
    dfa_obj = None

    def _do_string_test(dfa_obj):
        while True:
            test_str = input("Input string(empty input to quit): ")
            if_match = False
            err_msg = ''

            if test_str == '':
                return

            try:
                if_match = dfa_obj.match(test_str)
            except ValueError as e:
                err_msg = e.args[0]
            
            if if_match:
                print("\"{}\" match the regex.".format(test_str))
            else:
                print("\"{}\" does not match the regex. {}".format(test_str, err_msg))

    def _check_regex():
        if len(regex_str) > 0:
            return True
        else:
            print("No regular expression provided!")
            return False
    
    while True:
        print(menu.format(regex_str))
        choice = input("Your choice: ")
        if choice not in available_choices:
            print("Bad choice({})!".format(choice))
            continue
        if choice == '0':
            break
        elif choice == '1':
            regex_str = input('Input your regular expression: ')
            nfa_obj = NFA(regex_str)
            nfa_obj.compile()
            dfa_obj = DFA(nfa_obj)
            dfa_obj.compile()
            continue
        elif _check_regex():
            if choice == '2':
                _do_string_test(dfa_obj)
            elif choice == '3':
                nfa_obj.print_table()
            elif choice == '4':
                dfa_obj.print_table()
            elif choice == '5':
                dfa_obj.minimize()
            

    # nfa = NFA(example1)
    # nfa.compile()
    # print(nfa.nfa_table)
    # nfa.print_table()

    # dfa = DFA(nfa)
    # dfa.compile()
    # dfa.print_table()
    # dfa.minimize()
    # dfa.print_table()

    # print(dfa.match('abb'))