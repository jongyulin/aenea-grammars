import dragonfly

try:
    import aenea.communications
except ImportError:
    print 'Unable to import Aenea client-side modules.'
    raise

class DgnImported(dragonfly.RuleRef):
    """
        Base class that implements an imported rule and takes care of
        decoding recognitions accordingly.

    """

    def __init__(self, name=None, imported_name=None, default=None):
        if not imported_name:
            imported_name = name
        self.imported_name = imported_name
        self.imported_rule = dragonfly.Rule(self.imported_name, imported=True)
        dragonfly.RuleRef.__init__(self, self.imported_rule, name, default=default)

    def decode(self, state):
        state.decode_attempt(self)

        # Check that at least one word has been dictated, otherwise fail.
        if state.rule() != self.imported_name:
            state.decode_failure(self)
            return

        # Determine how many words have been dictated.
        count = 1
        while state.rule(count) == self.imported_name:
            count += 1

        # Yield possible states where the number of dictated words
        # gobbled is decreased by 1 between yields.
        for i in xrange(count, 0, -1):
            state.next(i)
            state.decode_success(self)
            yield state
            state.decode_retry(self)
            state.decode_rollback(self)

        # None of the possible states were accepted, failure.
        state.decode_failure(self)
        return

    def value(self, node):
        return node.words()

class DgnLettersRule(dragonfly.CompoundRule):
    spec   = "letters <dgnletters>"
    extras = [DgnImported("dgnletters")]

    def _process_recognition(self, node, extras):
        aenea.Text(text).execute()

grammar = dragonfly.Grammar('global')

grammar.add_rule(DgnLettersRule())

grammar.load()


# Unload function which will be called at unload time.
def unload():
    global grammar
    if grammar:
        grammar.unload()
    grammar = None
