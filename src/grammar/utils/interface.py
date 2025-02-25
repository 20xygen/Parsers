from typing import Set, Dict, Tuple, Optional
from src.grammar.grammar import Grammar, Rule
from src.grammar.utils.representor import Representor, valid_non_terminals, valid_symbols
from src.grammar.utils.representor import valid_non_terminals_list, valid_terminals_list
from src.grammar.errors import InvalidNonTerminal, InvalidGrammarSymbol


class NaiveRule:
    left: str
    right: str

    def __init__(self, left: str, right: str):
        if left not in valid_non_terminals:
            raise InvalidNonTerminal(f"Non-terminal symbol {left} is invalid.")
        if any([sym not in valid_symbols for sym in right]):
            raise InvalidGrammarSymbol(f"Symbol {left} is invalid.")
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


def naive_grammar_to_grammar(naive: NaiveGrammar) -> Tuple[Grammar, Representor]:
    rep = Representor(naive.terminals | naive.non_terminals)
    start = rep.as_non_terminal(naive.start)
    non_terminals = rep.non_terminals()
    terminals = rep.terminals()
    rules: Set[Rule] = set()
    for rule in naive.rules:
        left = rep.as_non_terminal(rule.left)
        right = tuple([rep.as_grammar_symbol(sym) for sym in rule.right])  # empty if right is an epsilon
        rules.add(Rule(left, right))
    return Grammar(non_terminals, terminals, start, rules), rep


def input_grammar() -> Tuple[Grammar, Representor]:
    naive = input_naive_grammar()
    return naive_grammar_to_grammar(naive)


def grammar_to_naive_grammar(grammar: Grammar, rep: Optional[Representor] = None) -> NaiveGrammar:
    if rep is None:
        rep = Representor()

        prepared_non_terminals = list(grammar.non_terminals)
        prepared_non_terminals.remove(grammar.start)
        prepared_valid_non_terminals_list = valid_non_terminals_list.copy()
        prepared_valid_non_terminals_list.remove('S')
        rep.add('S', grammar.start)
        for sym, non in zip(prepared_valid_non_terminals_list, prepared_non_terminals):
            rep.add(sym, non)

        prepared_terminals = list(grammar.terminals)
        for sym, term in zip(valid_terminals_list, prepared_terminals):
            rep.add(sym, term)

    rules = set()
    for rule in grammar.rules:
        left = rep.as_non_terminal_symbol(rule.left)
        right = ''.join([rep.as_symbol(obj) for obj in rule.right])
        rules.add(NaiveRule(left, right))

    return NaiveGrammar(rep.non_terminal_symbols(), rep.terminal_symbols(), 'S', rules)


def str_rule(rule: Rule, rep: Representor):
    ret = f"{rep.as_symbol(rule.left)} -> "
    ret += ''.join([rep.as_symbol(obj) for obj in rule.right])
    return ret


def print_naive_grammar(grammar: NaiveGrammar) -> None:
    print("Non-terminals:", ', '.join(sorted(list(grammar.non_terminals))))
    print("Terminals:", ', '.join(sorted(list(grammar.terminals))))
    print("Start:", grammar.start)

    rules: Dict[str, Set[str]] = dict()
    for rule in grammar.rules:
        if rule.left not in rules:
            rules[rule.left] = set()
        rules[rule.left].add(rule.right)
    print("Rules:")
    for left, rights in sorted(rules.items()):
        print(f"\t{left} -> {' | '.join([sym if len(sym) > 0 else 'ε' for sym in rights])}")


def print_grammar(grammar: Grammar) -> None:
    naive = grammar_to_naive_grammar(grammar)
    print_naive_grammar(naive)
