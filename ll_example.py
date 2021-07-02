from analyzer.grammar.parser.ll import LLOne

# 这是提前准备的测试数据
from tests.data_to_test_ll import LLTestDataWithRecursion

# 原始输入数据
test_set = LLTestDataWithRecursion.raw_set_test
# 词典
word_set = LLTestDataWithRecursion.word_set
# 测试用的输入
test_inputs = LLTestDataWithRecursion.test_inputs
# 初始状态
start_state = LLTestDataWithRecursion.start_state
# 构建分析器
ll_parser = LLOne(test_set,
                    word_list=word_set,
                    start=start_state)
# 测试
print("原始输入:")
for i in test_set:
    print(i)
print("初始状态:", start_state)

for testin, expect, epos in LLTestDataWithRecursion.test_inputs:
    result, pos = ll_parser.parse(testin)
    print("输入:", testin, "期望:", expect, "实际输出:", result, "正确:", expect == result)
