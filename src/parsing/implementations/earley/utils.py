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
    if Logger.mode and i > 1:
        print(f"a_access({outer}, {index}) cause adding more than one ({i}) elements.")
    return outer[index]


class DebuggerError(Exception):
    pass


class Logger:
    representor: Optional[Representor] = None
    mode: bool = False

    @staticmethod
    def set_mode(debug_mode: bool) -> None:
        Logger.mode = debug_mode

    @staticmethod
    def set_representor(representor: Representor) -> None:
        Logger.representor = representor

    @staticmethod
    def __accessed() -> None:
        if not Logger.mode:
            raise DebuggerError("Debug mode is disabled.")
        if Logger.representor is None:
            raise DebuggerError("Debug representor not set.")

    @staticmethod
    def make_string(obj: Any) -> str:  # can print Dict, Set, List, Situation and GrammarSymbol
        Logger.__accessed()
        if isinstance(obj, Situation):
            right = ''.join(
                [Logger.representor.as_symbol(obj.rule.right[i]) for i in range(len(obj.rule.right))])
            ret = f"({Logger.representor.as_symbol(obj.rule.left)} -> "
            ret += right[:obj.point] + '·' + right[obj.point:]
            ret += f", {obj.previous}, {obj.current})"
        elif isinstance(obj, GrammarSymbol):
            ret = Logger.representor.as_symbol(obj)
        elif isinstance(obj, set):
            ret = "Set {"
            for item in obj:
                ret += '\n\t' + Logger.make_string(item)
            ret += ' }'
        elif isinstance(obj, dict):
            ret = "Dict {"
            for key, value in obj.items():
                ret += '\n\t' + Logger.make_string(key) + ' : '
                ret += Logger.make_string(value)
            ret += ' }'
        elif isinstance(obj, list):
            if len(obj) > 0 and all(isinstance(item, GrammarSymbol) for item in obj):
                ret = '" '
                for item in obj:
                    ret += Logger.make_string(item)
                ret += ' "'
            else:
                ret = "List {"
                for item in obj:
                    ret += '\n\t' + Logger.make_string(item)
                ret += ' }'
        else:
            ret = str(obj)
        return ret

    @staticmethod
    def print(*args):
        if Logger.mode and Logger.representor is not None:
            for arg in args:
                print(Logger.make_string(arg))