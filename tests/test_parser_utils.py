from analyzer.grammar.parser.utils import *
from .data_to_test import ParserTestData


def test_first_class():
    result = get_first_set(ParserTestData.sample_set_test)
    ans = ParserTestData.first_set_test_ans
    for k in result.keys():
        assert result.get(k) == ans.get(k), k


def test_follow_class():
    result, _ = get_follow_set(ParserTestData.sample_set_test)
    ans = ParserTestData.follow_set_test_ans
    for k in ans.keys():
        assert result.get(k) == ans.get(k), k


def test_generate_children():
    children = generate_children(ParserTestData.sample_set_test)
    ans = ParserTestData.children_ans
    for k in children.keys():
        assert children.get(k) == ans.get(k), k


def test_generate_parents():
    children = generate_children(ParserTestData.sample_set_test)
    parents = generate_parents(children)
    ans = ParserTestData.parents_ans
    for k in ans.keys():
        assert parents.get(k) == ans.get(k), k


def test_prior_sort():
    input_data = ParserTestData.sample_set_test
    ans = ParserTestData.topological_like_order
    result = prior_sort(input_data)
    for k1, k2 in zip(result, ans):
        assert k1 == k2, result
