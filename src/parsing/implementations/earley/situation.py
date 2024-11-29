from src.grammar.grammar import Rule, GrammarSymbol, Terminal, NonTerminal
from typing import Optional, List


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

    def __eq__(self, other) -> bool:
        return (self.rule == other.rule and
                self.point == other.point and
                self.previous == other.previous and
                self.current == other.current)

    def __hash__(self) -> int:
        return hash((self.rule, self.point, self.previous, self.current))

    def __str__(self) -> str:
        return str((self.rule, self.point, self.previous, self.current))


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