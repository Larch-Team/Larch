from abc import ABC, abstractmethod
from collections import namedtuple, Counter
from typing import Any, Iterable, Union, NewType
from sentence import Sentence
from exrex import generate, getone
from re import escape as resc
import re

import ply.lex as plex
from ply.lex import LexError, TOKEN

token_type = NewType('Token', str)

LexerRule = namedtuple('LexerRule', ('constraints', 'type_', 'lexems'))

class _RegEx(str):
    pass

def RegEx(*obj: str) -> list[_RegEx]:
    return [_RegEx(i) for i in obj]

class LrchLexerError(Exception):
    pass


def join_items(tuples):
    d = {}
    for k, v in tuples:
        if k in d:
            d[k].extend(v)
        else:
            d[k] = list(v)
    return {k: tuple(v) for k, v in d.items()}


def sep_items(tuples):
    d = []
    if isinstance(tuples, dict):
        tuples = tuples.items()
    for k, v in tuples:
        if isinstance(v, (tuple, list)):
            d.extend([(k, i) for i in v])
        else:
            d.append((k, v))
    return tuple(d)


class Lexicon(object):
    STACK = []
    LITERALS = {'(', ')'}

    def __init__(self) -> None:
        super().__init__()
        self.rules = set()
        self.needs_casing = False

    def __setitem__(self, type_: str, lexems: Union[str, Iterable[str]]) -> None:
        if isinstance(lexems, str):
            self.rules.add(LexerRule(tuple(self.STACK), type_, (lexems,)))
            self.needs_casing |= lexems.isupper()
        elif isinstance(lexems, (list, tuple, set)):
            self.rules.add(LexerRule(tuple(self.STACK), type_, tuple(lexems)))
            self.needs_casing |= any((i.isupper() for i in lexems))


class BuiltLexer(object):

    def __init__(self, lex: Lexicon, **kwargs: dict[str, Any]) -> None:
        super().__init__()
        self.needs_casing = lex.needs_casing
        self.LITERALS = lex.LITERALS
        self.find_new = self._get_find_new(lex)

        lex_tokens = [(i, j) for i, j, _ in self._filter_constraints(lex, kwargs)]
        gen_tokens = [(i, j) for i, j, for_generation in self._filter_constraints(lex, kwargs) if for_generation]

        # Generate lexems
        
        self.generator_regexes = {key: self._regex_from_list(
            val, True) for key, val in join_items(gen_tokens).items()}
            
        # Recognize lexems

        keywords, regexes = {}, {}
        for key, val in sep_items(lex_tokens):
            if isinstance(val, _RegEx):
                if regexes.get(key):
                    regexes[key].append(str(val))
                else:
                    regexes[key] = [str(val)]
            else:
                keywords[val] = key

        self.lexer_regexes = {key: self._regex_from_list(
            val) for key, val in regexes.items()}

        class _Lex:
            _master_re = re
            literals = lex.LITERALS
            reserved = keywords
            tokens = [i for i in self.lexer_regexes] + list(set(reserved.values()))
            t_ignore = ' \t'

            def __init__(self) -> None:
                self.num_count = 0
                self.build()

            def t_error(self, t):
                raise LrchLexerError(f'{t} is not tokenizable')

            def build(self, **kwargs):
                self.lexer = plex.lex(object=self, **kwargs)

            def tokenize(self, s: str):
                self.lexer.input(s)
                while (i := self.lexer.token()):
                    if i.value in self.literals:
                        yield i.value
                    else:
                        yield f"{i.type}_{i.value}"

            @TOKEN(self._regex_from_list(reserved.keys(), True))
            def t_reserved(self, t):
                t.type = self.reserved[t.value]    # Check for reserved words
                return t
        
        for type_, lexems in sorted(self.lexer_regexes.items(), key=lambda x: len(x[1]), reverse=True):
            setattr(_Lex, f"t_{type_}", lexems)

        self.lexer = _Lex()

    @staticmethod
    def _regex_from_list(lst: list[str], escape: bool = False):
        if escape:
            return r"|".join((f"({resc(i)})" for i in sorted(lst, reverse=True)))
        else:
            return r"|".join((f"({i})" for i in sorted(lst, reverse=True)))

        
    @staticmethod
    def _filter_constraints(lex: Lexicon, satisfied: dict[str, Any]) -> Iterable[tuple[str, tuple[str]]]:
        NOT_CHECKED = 'find_new', 'no_generation'
        for def_constr, type_, lexems in lex.rules:
            rewritten_satisfied = sep_items(satisfied)
            if all((i in rewritten_satisfied for i in def_constr if i[0] not in NOT_CHECKED)):
                yield type_, lexems, any((i[0] == 'no_generation' for i in def_constr))

    @staticmethod
    def _get_find_new(lex: Lexicon) -> set[str]:
        """Zwraca zbiór wszystkim typów, które określono w kontekście find_new"""
        return {type_ for constraints, type_, _ in lex.rules if any((i[0] == 'find_new' for i in constraints))}

    def tokenize(self, formula: str) -> list[token_type]:
        """
        Dla danego ciągu znaków generuje listę tokenów

        :param formula: Ciąg znaków do przetworzenia
        :type formula: str
        :raises LrchLexerError: Nie znaleziono tokenu
        :return: Lista tokenów w formie `[typ]_[leksem]`
        :rtype: list[str]
        """
        if not self.needs_casing:
            formula = formula.lower()

        try:
            sentence = list(self.lexer.tokenize(formula))
        except LexError as e:
            raise LrchLexerError(e)
        else:
            return sentence

    def generate(self, sentence: Sentence, type_: str) -> token_type:
        """
        Generuje nowy token dla danego typu

        :param sentence: Zdanie, w którym zostanie użyty
        :type sentence: Sentence
        :param type_: Typ tokenu
        :type type_: str
        :return: Token w formie `[typ]_[leksem]`
        :rtype: str
        """
        assert type_ in self.generator_regexes, "Type doesn't exist in this Lexicon"
        if type_ in self.find_new:
            new_lexems = generate(self.generator_regexes[type_])
            used_lexems = sentence.getLexems()

            try:
                while (new_lex := next(new_lexems)) not in used_lexems:
                    pass
            except StopIteration:
                return None
            else:
                return f"{type_}_{new_lex}"

        else:
            counted = Counter(
                (l for t, l in sentence.getItems() if l == type_)).items()
            try:
                new_lex = max(counted, key=lambda x: x[1])[0]
            except ValueError:
                return getone(self.generator_regexes[type_])
            else:
                return f"{type_}_{new_lex}"


class RuleConstraint(ABC):

    @abstractmethod
    def __init__(self, tag: Any) -> None:
        super().__init__()
        self.tag = tag

    def __enter__(self) -> None:
        Lexicon.STACK.append((type(self).__name__, self.tag))
        return

    def __exit__(self, *args) -> None:
        Lexicon.STACK.pop()
        return
