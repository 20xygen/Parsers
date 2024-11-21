from src.grammar.utils.interface import NaiveGrammar, NaiveRule, print_grammar
from src.grammar.utils.interface import print_naive_grammar, naive_grammar_to_grammar, input_grammar
from src.grammar.grammar import Grammar, Rule, Terminal, NonTerminal


# Create grammar in a common way

start = NonTerminal()
left_bracket = Terminal()
right_bracket = Terminal()
brackets_rule = Rule(start, [left_bracket, start, right_bracket, start])
epsilon_rule = Rule(start, [])
grammar = Grammar({start}, {left_bracket, right_bracket}, start, {brackets_rule, epsilon_rule})

print_grammar(grammar)  # you can print it
print()


# Create grammar in a naive way

brackets_rule = NaiveRule('S', '(S)S')
epsilon_rule = NaiveRule('S', '')
naive_grammar = NaiveGrammar({'S'}, {'(', ')'}, 'S', {brackets_rule, epsilon_rule})

print_naive_grammar(naive_grammar)  # you can also print a naive one
print()

grammar = naive_grammar_to_grammar(naive_grammar)

print_grammar(grammar)  # non-naive one will differ
print()


# Create grammar by entering

# grammar = input_grammar()

# print()
# print_grammar(grammar)
