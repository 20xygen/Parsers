from typing import Set
from grammar import Grammar, Rule
from representor import Representor, valid_terminals, valid_non_terminals


class NaiveRule:
    left: str
    right: str

    def __init__(self, left: str, right: str):
        if left not in valid_non_terminals:
            raise ValueError(f"Non-terminal symbol {left} is invalid.")
        if any([sym not in valid_terminals for sym in right]):
            raise ValueError(f"Symbol {left} is invalid.")
        self.left = left
        self.right = right


class NaiveGrammar:
    non_terminals: Set[str]
    terminals: Set[str]
    start: str
    rules: Set[NaiveRule]

    def __init__(self, non_terminals: Set[str], terminals: Set[str], start: str, rules: Set[NaiveRule]):
        self.non_terminals = non_terminals.copy()
        self.terminals = terminals.copy()
        self.start = start
        self.rules = rules.copy()


def input_naive_grammar() -> NaiveGrammar:
    non_terminals_quantity, terminals_quantity, rules_quantity = map(int, input().split())
    non_terminals = set(input().strip())
    terminals = set(input().strip())
    rules = set()
    for i in range(rules_quantity):
        left, right = input().split('->')
        rules.add(NaiveRule(left.replace(' ', ''), right.replace(' ', '')))
    start = input()
    return NaiveGrammar(non_terminals, terminals, start, rules)


def naive_grammar_to_grammar(naive: NaiveGrammar) -> Grammar:
    rep = Representor(naive.terminals | naive.non_terminals)
    start = rep.as_non_terminal(naive.start)
    non_terminals = rep.non_terminals()
    terminals = rep.terminals()
    rules: Set[Rule] = set()
    for rule in naive.rules:
        left = rep.as_non_terminal(rule.left)
        right = list([rep.as_grammar_symbol(sym) for sym in rule.right])  # empty if right is an epsilon
        rules.add(Rule(left, right))
    return Grammar(non_terminals, terminals, start, rules)


def input_grammar() -> Grammar:
    naive = input_naive_grammar()
    return naive_grammar_to_grammar(naive)
