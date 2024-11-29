from src.grammar.utility.interface import NaiveGrammar, NaiveRule, print_grammar
from src.grammar.utility.interface import print_naive_grammar, naive_grammar_to_grammar
from src.grammar.grammar import Grammar, Rule, Terminal, NonTerminal
from src.parsing.parser import NaiveParser
from src.parsing.implementations.earley.parser import EarleyParser
from src.parsing.implementations.earley.utils import Logger


# Create grammar in a common way

start = NonTerminal()
left_bracket = Terminal()
right_bracket = Terminal()
brackets_rule = Rule(start, (left_bracket, start, right_bracket, start))
epsilon_rule = Rule(start, tuple())
grammar = Grammar({start}, {left_bracket, right_bracket}, start, {brackets_rule, epsilon_rule})

print_grammar(grammar)  # you can print it
print()


# Create grammar in a naive way

brackets_rule = NaiveRule('S', '(S)S')
epsilon_rule = NaiveRule('S', '')
naive_grammar = NaiveGrammar({'S'}, {'(', ')'}, 'S', {brackets_rule, epsilon_rule})

print_naive_grammar(naive_grammar)  # you can also print a naive one
print()

grammar, _ = naive_grammar_to_grammar(naive_grammar)

print_grammar(grammar)  # non-naive one will differ
print()


# Create grammar by entering

# grammar, _ = input_grammar()
#
# print()
# print_grammar(grammar)


# Parsing

parser = EarleyParser()
naive_parser = NaiveParser(parser)  # works with naive grammars and implements the class from the technical assignment

naive_parser.fit(naive_grammar)

# You can log the process of parsing

# Logger.set_debug_mode(True)
# naive_parser.representor.auto_add(parser.grammar.start)
# Logger.set_debug_representor(naive_parser.representor)

assert (naive_parser.predict("()(())") is True)
assert (naive_parser.predict("") is True)
assert (naive_parser.predict(")") is False)
assert (naive_parser.predict("()(") is False)

