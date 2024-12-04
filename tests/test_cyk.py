import unittest
from src.parsing.parser import NaiveParser, GrammarClassError
from src.parsing.implementations.earley.parser import EarleyParser
from tests.utils.loader import test_data
from typing import Dict, Any


class TestEarley(unittest.TestCase):
    naive: NaiveParser
    data: Dict[str, Any]  # Any = List[NaiveGrammar, GrammarClass, List[Dict[str, Union[str, bool]]]]

    def setUp(self):
        self.naive = NaiveParser(EarleyParser())
        self.data = test_data()

    def test_01_fit(self):
        for name, test in self.data.items():
            try:
                self.naive.fit(test[0])
            except GrammarClassError as e:
                self.fail(f"Test '{name}'. Parser failed on fitted stage: {e}.")

    def test_02_predict(self):
        for name, test_set in self.data.items():
            self.naive.fit(test_set[0])
            for test in test_set[2]:
                result = self.naive.predict(test['word'])
                self.assertEqual(test['result'], result,
                                 f"Test '{name}'. Prediction on '{test['word']}' is wrong.")


if __name__ == '__main__':
    unittest.main()
