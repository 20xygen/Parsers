from typing import List, Optional, Set, Tuple


class GrammarSymbol:
    pass


class Terminal(GrammarSymbol):
    pass


class NonTerminal(GrammarSymbol):
    pass


class Rule:
    left: NonTerminal
    right: Tuple[GrammarSymbol, ...]

    def __init__(self, left: NonTerminal, right: Tuple[GrammarSymbol, ...]):
        self.left = left
        self.right = right

    def __eq__(self, other) -> bool:
        return self.left == other.left and self.right == other.right

    def __hash__(self) -> int:
        return hash((self.left, self.right))


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
