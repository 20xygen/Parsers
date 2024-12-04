from src.grammar.grammar import Terminal, NonTerminal, GrammarSymbol
from typing import Dict, Union, Optional, Set
import string
from src.grammar.errors import InvalidGrammarSymbol


valid_terminals_list = list()
valid_terminals_list += string.ascii_lowercase.strip()
valid_terminals_list += string.digits.strip()
valid_terminals_list += "()+-*/".strip()
valid_non_terminals_list = list(string.ascii_uppercase.strip())

valid_terminals = set(valid_terminals_list)
valid_non_terminals = set(valid_non_terminals_list)
valid_symbols = valid_terminals | valid_non_terminals


class RepresentorError(Exception):
    pass


class RepresentorTypeError(RepresentorError, TypeError):
    pass


class RepresentorValueError(RepresentorError, ValueError):
    pass


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
            self.auto_add(symbol)

    def terminal_symbols(self) -> Set[str]:
        return set(self.symbol_to_terminal.keys())

    def non_terminal_symbols(self) -> Set[str]:
        return set(self.symbol_to_non_terminal.keys())

    def symbols(self) -> Set[str]:
        return self.terminal_symbols() | self.non_terminal_symbols()

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
            raise InvalidGrammarSymbol(f"Invalid pair of arguments")

    def get_available_non_terminal_symbol(self) -> Optional[str]:
        for non in valid_non_terminals_list:
            if non not in self.non_terminal_symbols():
                return non
        return None

    def get_available_terminal_symbol(self) -> Optional[str]:
        for term in valid_terminals_list:
            if term not in self.terminal_symbols():
                return term
        return None

    def auto_add(self, obj: Union[str, GrammarSymbol]) -> Union[GrammarSymbol, str]:
        if isinstance(obj, str):
            if obj in valid_terminals:
                if obj in self.symbols():
                    return self.symbol_to_terminal[obj]
                term = Terminal()
                self.add(obj, term)
                return term
            elif obj in valid_non_terminals:
                if obj in self.symbols():
                    return self.symbol_to_non_terminal[obj]
                non = NonTerminal()
                self.add(obj, non)
                return non
            else:
                raise InvalidGrammarSymbol(f"Symbol {obj} is invalid.")
        elif isinstance(obj, Terminal):
            if obj in self.terminals():
                return self.terminal_to_symbol[obj]
            symbol = self.get_available_terminal_symbol()
            if symbol is None:
                raise RepresentorValueError(f"Ran out of terminal symbols.")
            self.add(symbol, obj)
            return symbol
        elif isinstance(obj, NonTerminal):
            if obj in self.non_terminals():
                return self.non_terminal_to_symbol[obj]
            symbol = self.get_available_non_terminal_symbol()
            if symbol is None:
                raise RepresentorValueError(f"Ran out of non-terminal symbols.")
            self.add(symbol, obj)
            return symbol
        else:
            raise RepresentorTypeError(f"Invalid type: {type(obj)}.")

    def as_terminal_symbol(self, term: Terminal) -> str:
        return self.terminal_to_symbol[term]

    def as_non_terminal_symbol(self, non: NonTerminal) -> str:
        return self.non_terminal_to_symbol[non]

    def as_symbol(self, obj: GrammarSymbol) -> str:
        if isinstance(obj, NonTerminal):
            return self.as_non_terminal_symbol(obj)
        elif isinstance(obj, Terminal):
            return self.as_terminal_symbol(obj)
        else:
            raise RepresentorTypeError(f"Invalid argument type: {type(obj)}.")

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
            raise InvalidGrammarSymbol(f"Symbol {symbol} is invalid.")

    def is_known(self, obj: Union[GrammarSymbol, str]) -> bool:
        if isinstance(obj, Terminal):
            return obj in self.terminals()
        elif isinstance(obj, NonTerminal):
            return obj in self.non_terminals()
        elif isinstance(obj, str):
            return obj in self.symbols()
        else:
            raise RepresentorTypeError(f"Invalid argument type: {type(obj)}.")
