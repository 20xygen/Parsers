from src.grammar.grammar import Grammar, Terminal, NonTerminal, GrammarSymbol, Rule
from src.parsing.parser import Parser, GrammarClass, ParserError
from typing import List, Set, Dict, Optional
from src.parsing.implementations.cyk.chomsky import ChomskyNormalizer


class CYKParser(Parser):
    grammar_class: GrammarClass
    grammar: Optional[Grammar]
    predicts: Dict[NonTerminal, List[List[bool]]]

    def __init__(self) -> None:
        self.grammar_class = GrammarClass("Context-free")
        self.grammar = None
        self.predicts = {}

    def fit(self, grammar: Grammar) -> None:
        normalizer = ChomskyNormalizer()
        self.grammar = normalizer.normalize(grammar)

    def __base(self, word: List[Terminal]) -> None:
        terms = self.grammar.terminals | set(word)
        terms_to_nons: Dict[Terminal, Set[NonTerminal]] = {term: set() for term in terms}
        for rule in self.grammar.rules:
            if len(rule.right) == 1 and isinstance(rule.right[0], Terminal):
                terms_to_nons[rule.right[0]].add(rule.left)
        for i, term in enumerate(word):
            for non in terms_to_nons[term]:
                self.predicts[non][i][i] = True

    def __deduces_epsilon(self):
        return Rule(self.grammar.start, ())

    def __step(self, length: int, word: List[Terminal]) -> None:
        for start in range(0, len(word) - length + 1):
            end = start + length - 1
            for mid in range(start, end):  # in A -> BC, C -> u the |u| is at least 1 (because C != S)
                for rule in self.grammar.rules:
                    if len(rule.right) == 2:  # A -> BC
                        left: NonTerminal = rule.left
                        first: NonTerminal = rule.right[0]
                        second: NonTerminal = rule.right[1]
                        self.predicts[left][start][end] |= (self.predicts[first][start][mid] and
                                                            self.predicts[second][mid + 1][end])

    def predict(self, word: List[Terminal]) -> bool:
        if self.grammar is None:
            raise ParserError("Parser is not fit.")

        if len(word) == 0:
            return Rule(self.grammar.start, ()) in self.grammar.rules

        self.predicts = {}
        for non in self.grammar.non_terminals:
            self.predicts[non] = [[False for _ in range(len(word))] for __ in range(len(word))]

        # Base of induction:

        self.__base(word)  # epsilon could be deduced only by S (and there is no S in rule.right when grammar in CNF)

        # Step of induction:

        for length in range(2, len(word) + 1):  # ... so, with rule A -> BC neither B nor C deduces epsilon
            self.__step(length, word)

        return self.predicts[self.grammar.start][0][len(word) - 1]
