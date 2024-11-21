from src.grammar.grammar import Grammar


valid_grammar_classes = [
    "Context-free",
    "LR(k)",
    "LR(1)",
    "LR(0)",
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

    def __str__(self):
        return valid_grammar_classes[self.category]


class Parser:
    grammar_class: GrammarClass

    def fit(self, grammar: Grammar) -> None:
        pass

    def predict(self, word: str) -> bool:
        pass


class GrammarClassError(Exception):
    pass
