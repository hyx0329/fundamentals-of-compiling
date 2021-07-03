from analyzer.grammar.parser.ll import LLOne
from tests.utils import print_table

# # 这是提前准备的测试数据
# from tests.data_to_test_ll import LLTestDataWithRecursion

# # 原始输入数据
# test_set = LLTestDataWithRecursion.raw_set_test
# # 词典
# word_set = LLTestDataWithRecursion.word_set
# # 测试用的输入
# test_inputs = LLTestDataWithRecursion.test_inputs
# # 初始状态
# start_state = LLTestDataWithRecursion.start_state
# # 构建分析器
# ll_parser = LLOne(test_set,
#                     word_list=word_set,
#                     start=start_state)
# # 测试
# print("原始输入:")
# for i in test_set:
#     print(i)
# print("初始状态:", start_state)

# for testin, expect, epos in LLTestDataWithRecursion.test_inputs:
#     result, pos = ll_parser.parse(testin)
#     print("输入:", testin, "期望:", expect, "实际输出:", result, "正确:", expect == result)

if __name__ == "__main__":
    rules = list()
    symbols = set()

    i = 1
    while True:
        rule = input('Your rule #{}(stop by empty input):'.format(i))
        if len(rule) == 0:
            break
        i += 1
        rules.append(rule)

    start_state = input('Your initial state:')

    syms = input("Your symbols(seperated by commas):")
    symbols.update(syms.split(','))
    symbols.difference_update(set(['']))
    
    ll_parser = LLOne(rules, symbols, start_state)
    mapper = ll_parser.parser.mapper
    mapper_length = len(mapper)
    parsing_table = ll_parser.parsing_table

    def map_to_real2(x):
        if isinstance(x, int):
            if x < 0:
                return 'eps'
            elif x < mapper_length:
                return mapper[x]
        return x

    print('Parsing table:')
    print_table(
        ll_parser.pindex_n, 
        ll_parser.pindex_t,
        ll_parser.parsing_table,
        map_to_real2,
        map_to_real2,
        map_to_real2
    )

    while True:
        string = input("Test string(empty to quit):")
        if len(string) == 0:
            break
        result, sym = ll_parser.parse(string)
        if result:
            print('Good input!')
        else:
            print('Bad input at symbol "{}".'.format(sym))
