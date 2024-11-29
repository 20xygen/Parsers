from src.grammar.grammar import Grammar, Rule, GrammarSymbol, Terminal, NonTerminal
from typing import Optional, List, Dict, Set
from src.parsing.parser import Parser, GrammarClass, ParserError
from src.parsing.implementations.earley.situation import Situation, SituationFactory
from src.parsing.implementations.earley.utils import a_access, a_add, Logger


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
        self.rules = {}
        for rule in self.grammar.rules:
            if rule.left not in self.rules.keys():
                self.rules[rule.left] = set()
            self.rules[rule.left].add(rule)

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

    def __get_start(self) -> Situation:
        return Situation(self.__basic_rule(), 0, 0, 0)

    def __get_target(self, word_length: int) -> Situation:
        return Situation(self.__basic_rule(), 1, 0, word_length)

    @staticmethod
    def __predict(rule: Rule,
                  situation_map: Dict[Optional[GrammarSymbol], Set[Situation]],
                  result_map: Dict[Optional[GrammarSymbol], Set[Situation]]) -> bool:
        if rule.left not in situation_map.keys():
            return False
        ret = False
        if rule.left in situation_map.keys():
            for sit in situation_map[rule.left]:
                predicted = SituationFactory.predict(sit, rule)
                if predicted is not None:
                    a_add(result_map, predicted.next_symbol(), predicted)
                    ret = True
        return ret

    @staticmethod
    def __complete(parents_map: Dict[Optional[GrammarSymbol], Set[Situation]],
                   kid_iterable: Set[Situation],
                   result_map: Dict[Optional[GrammarSymbol], Set[Situation]]) -> bool:
        ret = False
        for kid in kid_iterable:
            if kid.rule.left in parents_map.keys():
                for parent in parents_map[kid.rule.left]:
                    completed = SituationFactory.complete(parent, kid)
                    if completed is not None:
                        ret = True
                        a_add(result_map, completed.next_symbol(), completed)
        return ret

    @staticmethod
    def __complete_ancestors(space: List[Dict[Optional[GrammarSymbol], Set[Situation]]],
                             kids_iterable: Set[Situation],
                             result_map: Dict[Optional[GrammarSymbol], Set[Situation]]) -> bool:
        ret = False
        for kid in kids_iterable:
            if kid.previous < kid.current:
                parents_map = space[kid.previous]
                if kid.rule.left in parents_map.keys():
                    for parent in parents_map[kid.rule.left]:
                        completed = SituationFactory.complete(parent, kid)
                        if completed is not None:
                            ret = True
                            a_add(result_map, completed.next_symbol(), completed)
        return ret

    def __closure(self,
                  cell: Dict[Optional[GrammarSymbol], Set[Situation]],
                  everything: Set[Situation],
                  space: List[Dict[Optional[GrammarSymbol], Set[Situation]]]):

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

                # With the previous cells:
                if None in layers[target - 1].keys():
                    self.__complete_ancestors(space, layers[target - 1][None], a_access(layers, target))

                # With the current cell:
                layers.append({})
                for i in range(0, target):
                    if None in layers[target - 1].keys():
                        self.__complete(layers[i], layers[target - 1][None], a_access(layers, target))
                    if None in layers[i].keys():
                        self.__complete(layers[target - 1], layers[i][None], a_access(layers, target))

                for key, value in layers[target].items():
                    value.difference_update(everything)  # removes copies
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
                            self.__predict(rule, layers[i], a_access(layers, target))
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
    def __scan(space: List[Dict[Optional[GrammarSymbol], Set[Situation]]],
               position: int,
               word: List[Terminal]) -> bool:
        ret = False
        Logger.print(f"\nStep {position}:", a_access(space, position))
        if word[position] in space[position].keys():
            for sit in space[position][word[position]]:
                scanned = SituationFactory.scan(sit, word)
                if scanned is not None:
                    a_add(a_access(space, position + 1), scanned.next_symbol(), scanned)
                    ret = True
        Logger.print(f"Scanned prefix ({position}):", word[:position + 1])
        Logger.print(f"After scan:", a_access(space, position + 1))
        return ret

    def predict(self, word: List[Terminal]) -> bool:
        if self.grammar is None or self.rules is None or self.original_start is None:
            raise ParserError("Parser is not fit before prediction.")

        Logger.print("Starting prediction of this word:", word)

        space: List[Dict[Optional[GrammarSymbol], Set[Situation]]] = list()

        space.append({})
        space[0][self.__original_start()] = {self.__get_start()}
        everything = space[0][self.__original_start()].copy()

        self.__closure(space[0], everything, space)

        for position in range(len(word)):
            self.__scan(space, position, word)
            for key, value in a_access(space, position + 1).items():
                everything.difference_update(value)

            self.__closure(space[position + 1], everything, space)

        Logger.print("\nLet's see what we have at the end:", everything, '')

        return self.__get_target(len(word)) in everything
