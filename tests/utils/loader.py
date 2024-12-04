import json
from pathlib import Path
from typing import List, Dict, Union, Any
from src.grammar.grammar import Grammar
from src.grammar.utils.interface import NaiveGrammar, NaiveRule, naive_grammar_to_grammar
from src.parsing.parser import GrammarClass


tests_folder = Path(__file__).parent.parent / "data"
tests_file = tests_folder / "test_data.json"


def load_tests() -> Dict[str, Any]:  # Any = List[NaiveGrammar, GrammarClass, List[Dict[str, Union[str, bool]]]]
    with open(tests_file, "r") as file:
        data = json.load(file)
    result = {}
    for name, test in data.items():
        rules = [NaiveRule(rule["left"], rule["right"]) for rule in test["grammar"]["rules"]]
        naive = NaiveGrammar(set(test["grammar"]["non_terminals"]),
                             set(test["grammar"]["terminals"]),
                             test["grammar"]["start"],
                             set(rules))
        result[name] = [naive,
                        GrammarClass(test["grammar_class"]) if test["grammar_class"] is not None else GrammarClass("Unknown"),
                        test["tests"]]
    return result


test_cache = None


def test_data() -> Dict[str, Any]:
    global test_cache
    if test_cache is None:
        test_cache = load_tests()
    return test_cache
