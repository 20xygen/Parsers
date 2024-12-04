from src.grammar.grammar import Grammar
from src.grammar.utils.interface import input_naive_grammar, print_naive_grammar
from src.parsing.parser import NaiveParser, Parser
from typing import Type


def interactive_parsing(parser_class: Type[Parser], comments: bool = False) -> None:
    if comments:
        print(f"Input your grammar and words to predict by {parser_class.__name__}:")

    grammar = input_naive_grammar()
    words = []
    quantity = int(input())
    for _ in range(quantity):
        words.append(input())

    if comments:
        print("\nYour grammar:\n")
        print_naive_grammar(grammar)

    parser = parser_class()
    naive = NaiveParser(parser)
    naive.fit(grammar)

    if comments:
        print("\nPredictions:\n")

    for word in words:
        result = naive.predict(word)
        if comments:
            print(f"{word}: {'Yes' if result else 'No'}")
        else:
            print('Yes' if result else 'No')


def infinite_interactive_parsing(parser_class: Type[Parser], comments: bool = False) -> None:
    number = 1
    while True:
        if comments:
            print(f"\n\nTest number {number}:\n")
        interactive_parsing(parser_class, comments)
        number += 1
