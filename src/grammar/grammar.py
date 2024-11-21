from typing import List, Optional, Set


class GrammarSymbol:
    pass


class Terminal(GrammarSymbol):
    pass


class NonTerminal(GrammarSymbol):
    pass


class Rule:
    left: NonTerminal
    right: List[GrammarSymbol]

    def __init__(self, left: NonTerminal, right: List[GrammarSymbol]):
        self.left = left
        self.right = right.copy()  # non-deep copy


class Grammar:  # Context free
    non_terminals: Set[NonTerminal]
    terminals: Set[Terminal]
    start: NonTerminal
    rules: Set[Rule]

    def __init__(self, non_terminals: Set[NonTerminal], terminals: Set[Terminal], start: NonTerminal, rules: Set[Rule]):
        self.non_terminals = non_terminals.copy()
        self.terminals = terminals.copy()
        self.start = start
        self.rules = rules.copy()
