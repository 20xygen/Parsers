from grammar import Terminal, Grammar, NonTerminal, Rule, GrammarSymbol
from typing import Dict, Union, Optional, List, Set, Tuple
import string


valid_terminals = set()
valid_terminals += set(string.ascii_lowercase.strip())
valid_terminals += set(string.digits.strip())
valid_terminals += set("()+-*/".strip())

valid_non_terminals = set(string.ascii_uppercase.strip())

valid_symbols = valid_terminals | valid_non_terminals


class Representor:
    symbol_to_terminal: Dict[str, Terminal]
    terminal_to_symbol: Dict[Terminal, str]
    symbol_to_non_terminal: Dict[str, NonTerminal]
    non_terminal_to_symbol: Dict[NonTerminal, str]

    def __init__(self, data: Optional[Set[str]] = None):
        self.symbol_to_terminal = dict()
        self.terminal_to_symbol = dict()
        self.symbol_to_non_terminal = dict()
        self.non_terminal_to_symbol = dict()
        if data is not None:
            self.fill(data)

    def fill(self, data: Set[str]):
        for symbol in data:
            self.add(symbol)

    def symbols(self) -> Set[str]:
        return set(self.symbol_to_terminal.keys()).union(self.symbol_to_non_terminal.keys())

    def terminals(self) -> Set[Terminal]:
        return set(self.terminal_to_symbol.keys())

    def non_terminals(self) -> Set[NonTerminal]:
        return set(self.non_terminal_to_symbol.keys())

    def add(self, symbol: str, obj: Union[Terminal, NonTerminal]) -> None:
        if symbol in valid_terminals and isinstance(obj, Terminal):
            self.symbol_to_terminal[symbol] = obj
            self.terminal_to_symbol[obj] = symbol
        elif symbol in valid_non_terminals and isinstance(obj, NonTerminal):
            self.symbol_to_non_terminal[symbol] = obj
            self.non_terminal_to_symbol[obj] = symbol
        else:
            raise TypeError(f"Invalid pair of arguments")

    def add(self, symbol: str) -> GrammarSymbol:
        if symbol in valid_terminals:
            if symbol in self.symbols():
                return self.symbol_to_terminal[symbol]
            term = Terminal()
            self.add(symbol, term)
            return term
        elif symbol in valid_non_terminals:
            if symbol in self.symbols():
                return self.symbol_to_non_terminal[symbol]
            non = NonTerminal()
            self.add(symbol, non)
            return non
        else:
            raise ValueError(f"Symbol {symbol} is invalid.")

    def as_symbol(self, term: Terminal) -> str:
        return self.terminal_to_symbol[term]

    def as_terminal(self, symbol: str) -> Terminal:
        return self.symbol_to_terminal[symbol]

    def as_non_terminal(self, symbol: str) -> NonTerminal:
        return self.symbol_to_non_terminal[symbol]

    def as_grammar_symbol(self, symbol: str) -> GrammarSymbol:
        if symbol in valid_terminals:
            return self.as_terminal(symbol)
        elif symbol in valid_non_terminals:
            return self.as_non_terminal(symbol)
        else:
            raise ValueError(f"Symbol {symbol} is invalid.")


