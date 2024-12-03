from src.grammar.grammar import Grammar, Terminal
from typing import List, Optional
from src.grammar.utility.interface import NaiveGrammar, naive_grammar_to_grammar
from src.grammar.utility.representor import Representor


valid_grammar_classes = [
    "Context-free",
    "LR(k)",
    "LR(1)",
    "LR(0)",
    "Unknown"
]


class GrammarClass:
    category: int

    def __init__(self, class_name: str):
        if class_name not in valid_grammar_classes:
            raise ValueError(f"Grammar class {class_name} is not valid.")
        self.category = valid_grammar_classes.index(class_name)

    def __str__(self):
        return valid_grammar_classes[self.category]

    def __le__(self, other):
        return self.category <= other.category

    def __ge__(self, other):
        return self.category >= other.category

    def __eq__(self, other):
        return self.category == other.category

    def __str__(self):
        return valid_grammar_classes[self.category]


class Parser:
    grammar_class: GrammarClass

    def fit(self, grammar: Grammar) -> None:
        pass

    def predict(self, word: List[Terminal]) -> bool:
        pass


class GrammarClassError(Exception):
    pass


class ParserError(Exception):
    pass


class NaiveParser:  # Facade
    parser: Parser
    representor: Optional[Representor]

    def __init__(self, parser: Parser):
        self.parser = parser
        self.representor = None

    def __translate(self, word: str) -> List[Terminal]:
        if self.representor is None:
            raise ParserError("Representor is not initialized.")
        translated = []
        for symbol in word:
            if not self.representor.is_known(symbol):
                term = Terminal()
                self.representor.add(symbol, term)
            else:
                term = self.representor.as_terminal(symbol)
            translated.append(term)
        return translated

    def fit(self, naive: NaiveGrammar) -> None:
        grammar, representor = naive_grammar_to_grammar(naive)
        self.representor = representor
        self.parser.fit(grammar)

    def predict(self, word: str) -> bool:
        translated = self.__translate(word)
        return self.parser.predict(translated)

    def grammar_class(self) -> GrammarClass:
        return self.parser.grammar_class
