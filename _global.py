try:
    from aenea import *
except ImportError:
    print 'Unable to import Aenea client-side modules.'
    raise


def greeter(name):
    Text(name.format()).execute()

def cap_greeter(name):
    name=name.format()
    name[0]=name[0].capitalize()
    Text(name).execute()

def right_mouse(n, m):
    distance = n * 100 + m * 10
    Mouse("<%(distance)d, 0>").execute()

def louse(n):
    n = n * -1
    Mouse("<" + str(n) + ", 0>").execute()

def toss(n):
    n = n * -1
    Mouse("<0, " + str(n) + ">").execute()

class Phrase(MappingRule):
    mapping = {
        'phrase <name>': Function(greeter)
        #'cap phrase <name>': Function(cap_greeter)
        }
    extras = [Dictation(name='name')]

class MyMouse(MappingRule):
    mapping = {
        'click': Mouse("left"),
        'click twice': Mouse("left:2"),
        'click right': Mouse("right"),
        'rouse [<n>]': Mouse("<%(n)d, 0>"),
        'douse [<n>]': Mouse("<0, %(n)d>"),
        'louse [<n>]': Function(louse),
        'toss [<n>]': Function(toss)
        }
    extras = [Integer("n", 1, 1500), Integer("m", 0, 9)]

class Movement(MappingRule):
    mapping = {
        'left [<n>]': Key('left:%(n)d'),
        'up [<n>]': Key('up:%(n)d'),
        'right [<n>]': Key('right:%(n)d'),
        'down [<n>]': Key('down:%(n)d'),
        'backspace [<n>]': Key('backspace:%(n)d'),
        'space [<n>]': Key('space:%(n)d'),
        'exam [<n>]': Key('x:%(n)d')
    }
    extras = [Integer("n", 1, 20)]

class EmacsIdentifiers(CompoundRule):
    spec = '<naming> <text>'
    extras = [
        Choice('naming', {
            # [
            #   lower(false)/upper(true) all first,
            #   cap first word, cap other words,
            #   separator
            # ]
            'constant': [ True, False, False, '_' ],
            'lisp': [ False, False, False, '-' ],
            'lower camel': [ False, False, True, '' ],
            'score': [ False, False, False, '_' ],
            'upper camel': [ False, True, True, '' ],
            'lower spaced': [ False, False, False, ' ' ]
        }),
        Dictation('text')
    ]

    def _process_recognition(self, node, extras):
        spec = extras['naming']
        text = extras['text'].format()
        text = text.upper() if spec[0] else text.lower()
        words = text.split(' ')
        if len(words) == 0: return
        if spec[1]: words[0]=words[0].capitalize()
        if spec[2]: words=[words[0]] + [w.capitalize() for w in words[1:]]
        Text(spec[3].join(words)).execute()

vocab=aenea.vocabulary.register_dynamic_vocabulary('spelling')
class DoubleRule(CompoundRule):
    spec = '<dynamic1> <dynamic2>'

    extras = [
        DictListRef('dynamic1', vocab),
        DictListRef('dynamic2', vocab)
        ]

    def _process_recognition(self, node, extras):
        extras['dynamic1'].execute(extras)
        extras['dynamic2'].execute(extras)

grammar = Grammar('global')

grammar.add_rule(Phrase())
grammar.add_rule(EmacsIdentifiers())
grammar.add_rule(MyMouse())
grammar.add_rule(Movement())
grammar.add_rule(DoubleRule())
grammar.load()


# Unload function which will be called at unload time.
def unload():
    global grammar
    if grammar:
        grammar.unload()
    grammar = None
