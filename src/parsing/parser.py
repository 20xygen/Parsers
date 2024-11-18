from src.grammar.grammar import Grammar


valid_language_classes = [
    "Context-free",
    "LR(k)",
    "LR(1)",
    "LR(0)",
]


class LanguageClass:
    category: int

    def __init__(self, class_name: str):
        if class_name not in valid_language_classes:
            raise ValueError(f"Language class {class_name} is not valid.")
        self.category = valid_language_classes.index(class_name)

    def __str__(self):
        return valid_language_classes[self.category]

    def __le__(self, other):
        return self.category <= other.category

    def __ge__(self, other):
        return self.category >= other.category


class Parser:
    language_class: LanguageClass

    def fit(self, grammar: Grammar):
        pass

    def predict(self, word: str) -> bool:
        pass
