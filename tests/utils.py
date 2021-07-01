def print_table(rlabel, clabel, content, mapper=lambda x: x):
    """打印表格"""
    assert isinstance(rlabel, list), "No row label found!"
    assert isinstance(clabel, list), "No colume lable found!"
    assert len(content) == len(rlabel), "Invalid result !"


    format_string = "{:>5}"

    print()
    # 表头
    print('|', end='')
    print(format_string.format('=====') + '|', end='')
    for _ in clabel:
        print(format_string.format('====='), end='')
    print('|')
    print('|', end='')
    print(format_string.format('') + '|', end='')
    for query in clabel:
        to_print = mapper(query)
        print(format_string.format(to_print), end='')
    print('|')
    print('|', end='')
    print(format_string.format('-----') + '|', end='')
    for _ in clabel:
        print(format_string.format('-----'), end='')
    print('|')

    # 内容
    for label, cont in zip(rlabel,content):
        print('|', end='')
        to_print = mapper(label)
        print(format_string.format(to_print), end='')
        print('|', end='')

        for v in cont:
            if v is None:
                print(format_string.format(' '), end='')
            else:
                to_print = ''.join(map(mapper, v))
                print(format_string.format(to_print), end='')
        print('|')

    # 尾巴分割线
    print('|', end='')
    print(format_string.format('=====') + '|', end='')
    for _ in clabel:
        print(format_string.format('====='), end='')
    print('|')

