import json
from pathlib import Path
from typing import List, Dict, Union, Any
from src.grammar.grammar import Grammar
from src.grammar.utils.interface import NaiveGrammar, NaiveRule, naive_grammar_to_grammar
from src.parsing.parser import GrammarClass


tests_folder = Path(__file__).parent.parent / "data"
tests_file = tests_folder / "test_data.json"


def load_tests() -> Dict[str, Any]:  # Any = List[Grammar, GrammarClass, List[Dict[str, Union[str, bool]]]]
    with open(tests_file, "r") as file:
        data = json.load(file)
    result = {}
    for name, test in data.items():
        rules = [NaiveRule(rule["left"], rule["right"]) for rule in test["grammar"]["rules"]]
        naive = NaiveGrammar(set(test["grammar"]["non_terminals"]),
                             set(test["grammar"]["terminals"]),
                             test["grammar"]["start"],
                             set(rules))
        result[name] = [naive_grammar_to_grammar(naive),
                        GrammarClass(test["grammar_class"]),  # TODO: correct the grammar classes in test data
                        test["tests"]]
    return result
