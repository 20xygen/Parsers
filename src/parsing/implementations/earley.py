from src.grammar.grammar import Grammar, Rule, GrammarSymbol, Terminal, NonTerminal
from typing import Optional, List, Dict, Set, Any
from src.grammar.utility.representor import Representor
from src.parsing.parser import Parser, GrammarClass, ParserError
from src.grammar.utility.interface import print_grammar


debug_representor: Optional[Representor] = None
debug_mode = True


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
        if debug_representor is None:
            return str((self.rule, self.point, self.previous, self.current))
        right = ''.join([debug_representor.as_symbol(self.rule.right[i]) for i in range(len(self.rule.right))])
        ret = f"({debug_representor.as_symbol(self.rule.left)} -> "
        ret += right[:self.point] + '·' + right[self.point:]
        ret += f", {self.previous}, {self.current})"
        return ret


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
    original_start: Optional[NonTerminal]
    rules: Optional[Dict[NonTerminal, Set[Rule]]]

    def __init__(self):
        super().__init__()
        self.grammar_class = GrammarClass("Context-free")
        self.grammar = None
        self.rules = None
        self.original_start = None

    def fit(self, grammar: Grammar) -> None:
        new_start = NonTerminal()
        new_rule = Rule(new_start, (grammar.start,))
        self.original_start = grammar.start
        self.grammar = Grammar(grammar.non_terminals | {new_start},
                               grammar.terminals,
                               new_start,
                               grammar.rules | {new_rule})
        for rule in grammar.rules:
            if rule.left not in self.rules:
                self.rules[rule.left] = set()
            self.rules[rule.left].add(rule)

    def print(self, obj: Any = None) -> None:
        if obj is None:
            print("EarleyParser with grammar:")
            print_grammar(self.grammar)
        elif isinstance(obj, Situation):
            print(obj)
        elif isinstance(obj, set):
            for item in obj:
                print('\t', item)
        elif isinstance(obj, Dict):
            for key, value in obj.items():
                print(key, ':')
                print('\t', value)
        else:
            print(f"Can not print {type(obj)}.")

    def __basic_rule(self) -> Rule:
        if self.grammar is None or self.rules is None or self.original_start is None:
            raise ParserError("Parser is not fit.")
        return next(iter(self.rules[self.grammar.start]))

    def __original_start(self) -> NonTerminal:
        if self.grammar is None or self.rules is None or self.original_start is None:
            raise ParserError("Parser is not fit.")
        ret = self.__basic_rule().right[0]
        if not isinstance(ret, NonTerminal):
            raise ParserError("Fit incorrectly.")  # assume, it never happens
        return ret

    def __is_target(self, sit: Situation) -> bool:
        return sit.rule == self.__basic_rule() and sit.point == 1

    def __get_start(self) -> Situation:
        return Situation(self.__basic_rule(), 0, 0, 0)

    def __get_target(self, word_length: int) -> Situation:
        return Situation(self.__basic_rule(), 1, 0, word_length)

    @staticmethod
    def __predict(rule: Rule,
                  situation_map: Dict[Optional[GrammarSymbol], Set[Situation]],
                  result_map: Dict[Optional[GrammarSymbol], Set[Situation]]) -> bool:
        ret = False
        for sit in situation_map[rule.left]:
            predicted = SituationFactory.predict(sit, rule)
            if predicted is not None:
                if predicted.next_symbol() not in result_map.keys():
                    result_map[predicted.next_symbol()] = set()
                result_map[predicted.next_symbol()].add(predicted)
                ret = True
        return ret

    @staticmethod
    def __complete(parents_map: Dict[Optional[GrammarSymbol], Set[Situation]],
                   kid_iterable: Set[Situation],
                   result_map: Dict[Optional[GrammarSymbol], Set[Situation]]) -> bool:
        ret = False
        for kid in kid_iterable:
            for parent in parents_map[kid.rule.left]:
                completed = SituationFactory.complete(parent, kid)
                if completed is not None:
                    ret = True
                    if not completed.next_symbol() in result_map.keys():
                        result_map[completed.next_symbol()] = set()
                    result_map[completed.next_symbol()].add(completed)
        return ret

    @staticmethod
    def __scan(pool: Set[Situation], word: List[Terminal]):
        ret: Set[Situation] = set()
        for sit in pool:
            scanned = SituationFactory.scan(sit, word)
            if scanned is not None:
                ret.add(scanned)
        return ret

    def __closure(self,
                  cell: Dict[Optional[GrammarSymbol], Set[Situation]],
                  everything: Set[Situation]):

        layers: List[Dict[Optional[GrammarSymbol], Set[Situation]]] = [cell.copy()]

        target = 1
        start = 0

        # Complete & Predict global closure {

        global_changes = True
        while global_changes:
            global_changes = False

            # Complete closure {

            changes = True
            while changes:
                changes = False

                layers.append({})
                for i in range(0, target):
                    self.__complete(layers[i], layers[target - 1][None], layers[target])
                    self.__complete(layers[target - 1], layers[i][None], layers[target])

                for key, value in layers[target].items():
                    value.difference_update(everything)  # remove copies
                    if len(value) > 0:
                        global_changes = True
                        changes = True
                        everything.update(value)

                if changes:
                    target += 1

            # }

            # Predict on new ones {

            changes = True
            while changes:
                changes = False

                for non, rule_iterable in self.rules.items():
                    for rule in rule_iterable:
                        for i in range(start, target):
                            self.__predict(rule, layers[i], layers[target])
                start = target

                for key, value in layers[target].items():
                    value.difference_update(everything)  # remove copies
                    if len(value) > 0:
                        global_changes = True
                        changes = True
                        everything.update(value)

                if changes:
                    target += 1

            # }

        # }

        for i in range(1, target):
            for key, value in layers[i].items():
                if key not in cell.keys():
                    cell[key] = set()
                cell[key].update(value)

    @staticmethod
    def __step(space: List[Dict[Optional[GrammarSymbol], Set[Situation]]],
               position: int,
               word: List[Terminal]) -> bool:
        ret = False
        for sit in space[position][word[position]]:
            scanned = SituationFactory.scan(sit, word)
            if scanned is not None:
                if scanned.next_symbol() not in space[position + 1].keys():
                    space[position + 1][scanned.next_symbol()] = set()
                space[position + 1][scanned.next_symbol()].add(scanned)
                ret = True
        return ret

    def predict(self, word: List[Terminal]) -> bool:
        if self.grammar is None or self.rules is None or self.original_start is None:
            raise ParserError("Parser is not fit before prediction.")

        space: List[Dict[Optional[GrammarSymbol], Set[Situation]]] = []

        space[0] = {}
        space[0][self.__original_start()] = {self.__get_start()}
        everything = space[0][self.__original_start()].copy()

        self.__closure(space[0], everything)

        for position in range(len(word)):
            self.__step(space, position, word)
            for key, value in space[position + 1].items():
                everything.difference_update(value)

            self.__closure(space[position + 1], everything)

        return self.__get_target(len(word)) in everything
