"""
Transkrypcja basic.py na nowy format definicji języka
"""
from plugins.Lexicon.__utils__ import *

SOCKET = 'Lexicon'
VERSION = '0.0.1'

Lex = Lexicon()

with use_language('propositional'):
    with use_language('uses negation'):
        Lex['not'] = 'not', '~', '!'
    Lex['and'] = 'oraz', 'and', '^', '&'
    Lex['or'] = 'lub', 'or', '|', 'v'
    Lex['imp'] = 'imp', '->'
    with no_generation():
        Lex['sentvar'] = RegEx(r'\w+')
    with find_new():
        Lex['sentvar'] = RegEx(r'[a-z]')

with use_language('predicate'):
    Lex['forall'] = 'forall', '/\\', 'A'
    Lex['exists'] = 'exists', '\\/', 'E'
    with find_new():
        Lex['constant'] = RegEx(r'[a-t]', r'\d')
        Lex['indvar'] = RegEx(r'[u-z]')
        Lex['predicate'] = RegEx(r'[P-Z]')
        Lex['function'] = RegEx(r'[F-O]')

with use_language('sequent calculus'):
    Lex['turnstile'] = '=>', '\|-'
    Lex['sep'] = ';'
    Lex['falsum'] = 'bot', 'F'


def get_lexicon() -> Lexicon:
    return Lex