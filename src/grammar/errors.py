class GrammarError(Exception):
    pass


class InvalidGrammarSymbol(GrammarError):
    pass


class InvalidTerminal(InvalidGrammarSymbol):
    pass


class InvalidNonTerminal(InvalidGrammarSymbol):
    pass
