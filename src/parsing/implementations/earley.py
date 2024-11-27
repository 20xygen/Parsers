from src.grammar.grammar import Grammar, Rule, GrammarSymbol, Terminal, NonTerminal
from typing import Optional, List, Dict, Set
from src.grammar.utils.representor import Representor
from src.parsing.parser import Parser, GrammarClass


class Situation:
    rule: Rule
    point: int
    previous: int
    current: int

    def __init__(self, rule: Rule, point: int, previous: int, current: int):
        self.rule = rule
        self.point = point
        self.previous = previous
        self.current = current

    def is_completed(self) -> bool:
        return self.point == len(self.rule.right)

    def next_symbol(self) -> Optional[GrammarSymbol]:
        if self.is_completed():
            return None
        return self.rule.right[self.point]


class SituationFactory:
    @staticmethod
    def can_scan(situation: Situation, word: List[Terminal]) -> bool:
        return (not situation.is_completed() and
                isinstance(situation.next_symbol(), Terminal) and
                word[situation.current] == situation.next_symbol())

    @staticmethod
    def scan(situation: Situation, word: List[Terminal]) -> Optional[Situation]:
        if not SituationFactory.can_scan(situation, word):
            return None
        return Situation(situation.rule, situation.point + 1, situation.previous, situation.current + 1)

    @staticmethod
    def can_predict(situation: Situation, rule: Rule) -> bool:
        return (not situation.is_completed() and
                isinstance(situation.next_symbol(), NonTerminal) and
                rule.left == situation.next_symbol())

    @staticmethod
    def predict(situation: Situation, rule: Rule) -> Optional[Situation]:
        if not SituationFactory.can_predict(situation, rule):
            return None
        return Situation(rule, 0, situation.current, situation.current)

    @staticmethod
    def can_complete(parent: Situation, kid: Situation) -> bool:
        return (not parent.is_completed() and
                isinstance(parent.next_symbol(), NonTerminal) and
                parent.next_symbol() == kid.rule.left and
                parent.current == kid.previous)

    @staticmethod
    def complete(parent: Situation, kid: Situation) -> Optional[Situation]:
        if not SituationFactory.can_complete(parent, kid):
            return None
        return Situation(parent.rule, parent.point + 1, parent.previous, kid.current)


class EarleyParser(Parser):
    grammar: Optional[Grammar]
    rules: Dict[NonTerminal, Set[Rule]]

    def __init__(self):
        super().__init__()
        self.grammar_class = GrammarClass("Context-free")
        self.grammar = None

    def fit(self, grammar: Grammar) -> None:
        new_start = NonTerminal()
        new_rule = Rule(new_start, [grammar.start])
        self.grammar = Grammar(grammar.non_terminals | {new_start},
                               grammar.terminals,
                               new_start,
                               grammar.rules | {new_rule})
        for rule in grammar.rules:
            if rule.left not in self.rules:
                self.rules[rule.left] = set()
            self.rules[rule.left].add(rule)

    def predict(self, word: List[Terminal]) -> bool:
        pass  # TODO


