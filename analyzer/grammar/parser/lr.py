from .utils import *
from analyzer.lexer import GrammarLexer


class SLRAutomation:
    def __init__(self):
        self.firsts = None
        self.follows = None
        self.action_table = None
        self.goto_table = None
        self.non_terminals = None
        self.grammar = None

    def compile(self):
        pass

    def consume(self):
        """吃"""
        pass