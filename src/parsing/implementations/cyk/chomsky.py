from typing import Optional, Dict, Set, Tuple, List
from src.grammar.grammar import Grammar, Rule, NonTerminal, Terminal, GrammarSymbol
from src.grammar.utility.interface import print_grammar


log_mode = False


def set_log_mode(mode: bool):
    global log_mode
    log_mode = mode


class Handler:
    next: Optional['Handler']

    def __init__(self) -> None:
        self.next = None

    def set_next(self, handler: 'Handler') -> None:
        self.next = handler

    def handle(self, grammar: Grammar) -> None:
        if log_mode:
            print(f"After {self.__class__.__name__}.handle():")
            print_grammar(grammar)
            print()
        if self.next is not None:
            self.next.handle(grammar)


class StartOnTheRightEraser(Handler):
    def handle(self, grammar: Grammar) -> None:
        flag = any(any(sym == grammar.start for sym in rule.right) for rule in grammar.rules)

        if flag:
            start = NonTerminal()
            new_rules: Set[Rule] = {Rule(grammar.start, (start,))}

            for rule in grammar.rules:
                left = rule.left if rule.left != grammar.start else start
                right = tuple([sym if sym != grammar.start else start
                               for sym in rule.right])
                new_rules.add(Rule(left, right))

            grammar.rules = new_rules
            grammar.non_terminals.add(start)

        super().handle(grammar)


class ProduceAnalyzer:
    @staticmethod
    def _generate_dependencies(rules: Set[Rule],
                               dependencies: Dict[Rule, Set[NonTerminal]],
                               reverse: Dict[NonTerminal, Set[Rule]]) -> None:
        for rule in rules:
            dependencies[rule] = set()
            for sym in rule.right:
                if isinstance(sym, NonTerminal):
                    dependencies[rule].add(sym)
                    if sym not in reverse.keys():
                        reverse[sym] = set()
                    reverse[sym].add(rule)


class NonProducingEraser(Handler, ProduceAnalyzer):
    @staticmethod
    def __check(rule: Rule,
                dependencies: Dict[Rule, Set[NonTerminal]],
                reverse: Dict[NonTerminal, Set[Rule]],
                produces: Dict[NonTerminal, bool]) -> None:
        non = rule.left
        if len(dependencies[rule]) == 0 and not produces[non]:
            produces[non] = True
            if non in reverse.keys():  # nothing depends on some non-terminals
                for dependent in reverse[non]:
                    dependencies[dependent].remove(rule.left)
                    NonProducingEraser.__check(dependent, dependencies, reverse, produces, )

    def handle(self, grammar: Grammar) -> None:
        dependencies: Dict[Rule, Set[NonTerminal]] = {}
        reverse: Dict[NonTerminal, Set[Rule]] = {}
        produces: Dict[NonTerminal, bool] = {non: False for non in grammar.non_terminals}

        ProduceAnalyzer._generate_dependencies(grammar.rules, dependencies, reverse)

        for rule in grammar.rules:
            NonProducingEraser.__check(rule, dependencies, reverse, produces)

        new_non_terminals: Set[NonTerminal] = {non for non in grammar.non_terminals if produces[non]}
        new_rules: Set[Rule] = set()

        for rule in grammar.rules:
            if (produces[rule.left] and
                    all(isinstance(sym, Terminal) or (isinstance(sym, NonTerminal) and produces[sym])
                        for sym in rule.right)):
                new_rules.add(rule)

        grammar.non_terminals = new_non_terminals | {grammar.start}
        grammar.rules = new_rules

        super().handle(grammar)


class UnreachableEraser(Handler):
    @staticmethod
    def __check(non: NonTerminal,
                rules: Dict[NonTerminal, Set[Rule]],
                reachable: Dict[NonTerminal, bool]) -> None:
        if reachable[non]:
            return
        reachable[non] = True
        for rule in rules[non]:
            for sym in rule.right:
                if isinstance(sym, NonTerminal):
                    UnreachableEraser.__check(sym, rules, reachable)

    def handle(self, grammar: Grammar) -> None:
        reachable: Dict[NonTerminal, bool] = {non: False for non in grammar.non_terminals}
        rules: Dict[NonTerminal, Set[Rule]] = {}

        for rule in grammar.rules:
            if rule.left not in rules.keys():
                rules[rule.left] = set()
            rules[rule.left].add(rule)

        UnreachableEraser.__check(grammar.start, rules, reachable)

        new_non_terminals: Set[NonTerminal] = {non for non in grammar.non_terminals if reachable[non]}
        new_rules: Set[Rule] = {rule for rule in grammar.rules if reachable[rule.left]}

        grammar.non_terminals = new_non_terminals  # start is always reachable
        grammar.rules = new_rules

        super().handle(grammar)


class MixedRulesFixer(Handler):
    def handle(self, grammar: Grammar) -> None:  # does NOT remove unused Terminals
        added_rules: Set[Rule] = set()
        added_non_terminals: Set[NonTerminal] = set()

        useful: Set[Terminal] = {sym for rule in grammar.rules for sym in rule.right if isinstance(sym, Terminal)}
        terminal_clones: Dict[Terminal, NonTerminal] = {}

        for term in useful:
            non = NonTerminal()
            rule = Rule(non, (term,))
            added_rules.add(rule)
            added_non_terminals.add(non)
            terminal_clones[term] = non

        new_rules: Set[Rule] = added_rules.copy()

        for rule in grammar.rules:
            right: List[NonTerminal] = []
            for sym in rule.right:
                if isinstance(sym, NonTerminal):
                    right.append(sym)
                else:
                    right.append(terminal_clones[sym])  # sym is Terminal
            new_rules.add(Rule(rule.left, tuple(right)))

        grammar.non_terminals |= added_non_terminals
        grammar.rules = new_rules

        super().handle(grammar)


class LongRulesDecomposer(Handler):
    def handle(self, grammar: Grammar) -> None:
        added_non_terminals: Set[NonTerminal] = set()
        new_rules: Set[Rule] = set()

        for rule in grammar.rules:
            if len(rule.right) <= 2:
                new_rules.add(rule)
            else:
                right: List[NonTerminal] = list(rule.right)  # assume there is no terminals in right part of long rules

                tail: NonTerminal = right[-1]
                right.pop(len(rule.right) - 1)

                while len(right) > 1:
                    non = NonTerminal()
                    added_non_terminals.add(non)
                    new_rules.add(Rule(non, (right[-1], tail)))
                    tail = non
                    right.pop(len(right) - 1)

                new_rules.add(Rule(rule.left, (right[0], tail)))

        grammar.non_terminals |= added_non_terminals
        grammar.rules = new_rules

        super().handle(grammar)


class EpsilonProducingEraser(Handler, ProduceAnalyzer):
    @staticmethod
    def __check(rule: Rule,  # Rule whose right part consists only of NonTerminal-s
                dependencies: Dict[Rule, Set[NonTerminal]],
                reverse: Dict[NonTerminal, Set[Rule]],
                produces_epsilon: Dict[NonTerminal, bool],
                added_rules: Set[Rule]) -> None:

        rules_to_check: Set[Rule] = set()
        became_producing = False

        for non in rule.right:
            if produces_epsilon[non]:
                right: Tuple[GrammarSymbol, ...] = tuple([sym for sym in rule.right if sym != non])
                rules_to_check.add(Rule(rule.left, right))

        for added in rules_to_check:
            if added in dependencies.keys():  # process only new rules
                continue
            dependencies[added] = set()
            for non in added.right:
                dependencies[added].add(non)
                if non not in reverse.keys():
                    reverse[non] = set()
                reverse[non].add(added)

        if not produces_epsilon[rule.left] and all(produces_epsilon[non] for non in rule.right):
            produces_epsilon[rule.left] = True

            if rule.left in reverse.keys():  # nothing depends on some non-terminals
                for dependant in reverse[rule.left]:
                    EpsilonProducingEraser.__check(dependant, dependencies, reverse, produces_epsilon, added_rules)

        for added in rules_to_check:
            if added not in dependencies.keys():  # process only new rules
                EpsilonProducingEraser.__check(added, dependencies, reverse, produces_epsilon, added_rules)

        added_rules |= rules_to_check

    def handle(self, grammar: Grammar) -> None:
        dependencies: Dict[Rule, Set[NonTerminal]] = {}
        reverse: Dict[NonTerminal, Set[Rule]] = {}
        produces_epsilon: Dict[NonTerminal, bool] = {non: False for non in grammar.non_terminals}

        rules: Set[Rule] = {rule for rule in grammar.rules
                            if all(isinstance(sym, NonTerminal) for sym in rule.right)}

        ProduceAnalyzer._generate_dependencies(rules, dependencies, reverse)
        added_rules: Set[Rule] = set()

        for rule in rules:
            EpsilonProducingEraser.__check(rule, dependencies, reverse, produces_epsilon, added_rules)

        candidates: Set[Rule] = grammar.rules | added_rules
        new_rules = {rule for rule in candidates if len(rule.right) > 0}
        if produces_epsilon[grammar.start]:
            new_rules.add(Rule(grammar.start, ()))

        grammar.rules = new_rules

        super().handle(grammar)


class SingleRuleEraser(Handler):
    @staticmethod
    def __dfs(non: NonTerminal,
              right: Tuple[GrammarSymbol, ...],
              used: Dict[NonTerminal, bool],
              reverse_graph: Dict[NonTerminal, Set[NonTerminal]],
              added_rules: Set[Rule]) -> None:
        if used[non]:
            return
        used[non] = True
        for ancestor in reverse_graph[non]:
            added_rules.add(Rule(ancestor, right))
            SingleRuleEraser.__dfs(ancestor, right, used, reverse_graph, added_rules)

    def handle(self, grammar: Grammar) -> None:
        reverse_graph: Dict[NonTerminal, Set[NonTerminal]] = {non: set() for non in grammar.non_terminals}
        added_rules: Set[Rule] = set()
        used_template: Dict[NonTerminal, bool] = {non: False for non in grammar.non_terminals}

        for rule in grammar.rules:
            if len(rule.right) == 1 and isinstance(rule.right[0], NonTerminal):
                reverse_graph[rule.right[0]].add(rule.left)

        for rule in grammar.rules:
            if len(rule.right) == 2 or (len(rule.right) == 1 and isinstance(rule.right[0], Terminal)):
                SingleRuleEraser.__dfs(rule.left, rule.right, used_template.copy(), reverse_graph, added_rules)

        new_rules = {rule for rule in grammar.rules
                     if len(rule.right) != 1 or isinstance(rule.right[0], Terminal)}
        new_rules |= added_rules
        grammar.rules = new_rules

        super().handle(grammar)


class ChomskyNormalizer:
    handlers: List[Handler]

    def __init__(self) -> None:
        self.handlers = [
            StartOnTheRightEraser(),
            MixedRulesFixer(),
            LongRulesDecomposer(),
            EpsilonProducingEraser(),
            SingleRuleEraser(),
            NonProducingEraser(),
            UnreachableEraser()
        ]
        for i in range(len(self.handlers) - 1):
            self.handlers[i].set_next(self.handlers[i + 1])

    def normalize(self, grammar: Grammar) -> Grammar:
        self.handlers[0].handle(grammar)
        return grammar
