from src.grammar.grammar import Grammar, Rule, GrammarSymbol, Terminal, NonTerminal
from typing import Optional, List, Dict, Set, Any
from src.grammar.utility.representor import Representor
from src.parsing.implementations.earley.situation import Situation


def a_add(outer: Dict[Any, Set], key: Any, value: Any) -> None:
    if key not in outer.keys():
        outer[key] = set()
    outer[key].add(value)


def a_access(outer: List[Dict], index: int) -> Dict:
    i = 0
    while len(outer) <= index:
        i += 1
        outer.append({})
    if EarlyLogger.mode and i > 1:
        print(f"a_access({outer}, {index}) cause adding more than one ({i}) elements.")
    return outer[index]


class DebuggerError(Exception):
    pass


class EarlyLogger:
    representor: Optional[Representor] = None
    mode: bool = False

    @staticmethod
    def set_mode(debug_mode: bool) -> None:
        EarlyLogger.mode = debug_mode

    @staticmethod
    def set_representor(representor: Representor) -> None:
        EarlyLogger.representor = representor

    @staticmethod
    def __accessed() -> None:
        if not EarlyLogger.mode:
            raise DebuggerError("Debug mode is disabled.")
        if EarlyLogger.representor is None:
            raise DebuggerError("Debug representor not set.")

    @staticmethod
    def make_string(obj: Any) -> str:  # can print Dict, Set, List, Situation and GrammarSymbol
        EarlyLogger.__accessed()
        if isinstance(obj, Situation):
            right = ''.join(
                [EarlyLogger.representor.as_symbol(obj.rule.right[i]) for i in range(len(obj.rule.right))])
            ret = f"({EarlyLogger.representor.as_symbol(obj.rule.left)} -> "
            ret += right[:obj.point] + '·' + right[obj.point:]
            ret += f", {obj.previous}, {obj.current})"
        elif isinstance(obj, GrammarSymbol):
            ret = EarlyLogger.representor.as_symbol(obj)
        elif isinstance(obj, set):
            ret = "Set {"
            for item in obj:
                ret += '\n\t' + EarlyLogger.make_string(item)
            ret += ' }'
        elif isinstance(obj, dict):
            ret = "Dict {"
            for key, value in obj.items():
                ret += '\n\t' + EarlyLogger.make_string(key) + ' : '
                ret += EarlyLogger.make_string(value)
            ret += ' }'
        elif isinstance(obj, list):
            if len(obj) > 0 and all(isinstance(item, GrammarSymbol) for item in obj):
                ret = '" '
                for item in obj:
                    ret += EarlyLogger.make_string(item)
                ret += ' "'
            else:
                ret = "List {"
                for item in obj:
                    ret += '\n\t' + EarlyLogger.make_string(item)
                ret += ' }'
        else:
            ret = str(obj)
        return ret

    @staticmethod
    def print(*args):
        if EarlyLogger.mode and EarlyLogger.representor is not None:
            for arg in args:
                print(EarlyLogger.make_string(arg))