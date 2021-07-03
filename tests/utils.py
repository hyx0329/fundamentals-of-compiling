def print_table(rlabel,
                clabel,
                content,
                xmapper=lambda x: x,
                ymapper=lambda x: x,
                cmapper=lambda x: x):
    """打印表格"""
    assert isinstance(rlabel, list), "No row label found!"
    assert isinstance(clabel, list), "No colume lable found!"
    assert len(content) == len(rlabel), "Invalid result !"

    format_string = "{:>8}"
    double_line = '========'
    single_line = '--------'

    print()
    # 表头
    print('|', end='')
    print(format_string.format(double_line) + '|', end='')
    for _ in clabel:
        print(format_string.format(double_line), end='')
    print('|')
    print('|', end='')
    print(format_string.format('') + '|', end='')
    for query in clabel:
        to_print = xmapper(query)
        print(format_string.format(to_print), end='')
    print('|')
    print('|', end='')
    print(format_string.format(single_line) + '|', end='')
    for _ in clabel:
        print(format_string.format(single_line), end='')
    print('|')

    # 内容
    for label, cont in zip(rlabel,content):
        print('|', end='')
        to_print = ymapper(label)
        print(format_string.format(to_print), end='')
        print('|', end='')

        for v in cont:
            if v is None:
                print(format_string.format(' '), end='')
            elif isinstance(v, (tuple, list)):
                vs = map(cmapper, v)
                to_print = ''.join(map(str, vs))
                print(format_string.format(to_print), end='')
            elif isinstance(v, set):
                str_list = [''.join(map(str, i)) for i in v]
                to_print = ','.join(str_list)
                print(format_string.format(to_print), end='')
            else:
                print(format_string.format(' '), end='')
        print('|')

    # 尾巴分割线
    print('|', end='')
    print(format_string.format(double_line) + '|', end='')
    for _ in clabel:
        print(format_string.format(double_line), end='')
    print('|')

