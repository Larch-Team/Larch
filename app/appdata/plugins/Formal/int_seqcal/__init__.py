"""
Rachunek sekwentów z mechanizmem kontroli pętli na podstawie: 
Howe, J. M. (1997, May). Two loop detection mechanisms: a comparison. In International Conference on Automated Reasoning with Analytic Tableaux and Related Methods (pp. 188-200). Springer, Berlin, Heidelberg.

Dowody mogą czasem się nie udać.

Implementacja opisana w:
https://github.com/PogromcaPapai/Larch/blob/24e1391c183d08842aa0cf7df971eeb01a1a9885/media/int_seqcal%20-%20implementacja.pdf
"""
import typing as tp
from exceptions import RaisedUserMistake, UserMistake
import plugins.Formal.__utils__ as utils
from history import History
from plugins.Formal.int_seqcal.libs import list_parts
from rules import RULES, PRECEDENCE
from libs import is_sequent
from proof import Proof
from sentence import Sentence
from usedrule import UsedRule

SOCKET = 'Formal'
VERSION = '0.2.0'

def get_tags() -> tuple[str]:
    return 'sequent calculus', 'propositional'


def get_operator_precedence() -> dict[str, int]:
    """Zwraca siłę wiązania danych spójników, im wyższa, tym mocniej wiąże (negacja ma najwyższą przykładowo)"""
    return PRECEDENCE


def prepare_for_proving(statement: Sentence) -> Sentence:
    """Przygotowuje zdanie do dowodzenia - czyszczenie, dodawanie elementów"""
    statement = utils.reduce_brackets(statement)
    if 'turnstile_=>' not in statement:
        return utils.add_prefix(statement, 'turnstile', '=>')
    else:
        return statement


def check_closure(branch: list[Sentence], used: History) -> tp.Union[None, tuple[utils.close.Close, str]]:
    """Sprawdza możliwość zamknięcia gałęzi, zwraca obiekty zamknięcia oraz komunikat do wyświetlenia"""
    _, (left, right) = branch[-1].getComponents(PRECEDENCE)

    # Right part verification
    empty = len(right)==1

    # Left part verification
    if not left:
        return None
    for f in list_parts(left):

        # F, ... => ...
        if len(f)==1 and f[0].startswith("falsum_"):
            return utils.close.Falsum, "Falsum found on the left"

        # p, ... => p
        if f==right:
            return utils.close.Axiom, "Sequent on the right corresponds with a sequent on the left"

        # Detect finish
        empty &= not any((any((j.startswith(i) for j in f)) for i in ('and_', 'or_', 'imp_')))

    if empty:
        return utils.close.Emptiness, "Nothing more can be done with this branch, so it was closed."


def check_syntax(tokenized_statement: Sentence) -> tp.Union[UserMistake, None]:
    """Sprawdza poprawność zapisu tokenizowanego zdania, zwraca informacje o błędach w formule"""
    return None


def get_rules_docs() -> dict[str, str]:
    """Zwraca reguły rachunku z opisem"""
    return {
        name: "\n".join((rule.symbolic, rule.__doc__))
        for name, rule in RULES.items()
    }


def get_needed_context(rule_name: str) -> tuple[utils.ContextDef]:
    """Zwraca informacje o wymaganym przez daną regułę kontekście w formie obiektów ContextDef"""
    if (rule := RULES.get(rule_name, None)):
        return tuple(rule.context)
    else:
        return None


def solver(proof: Proof) -> bool:
    


def checker(rule: UsedRule, conclusion: Sentence) -> tp.Union[UserMistake, None]:
    """
    Na podstawie informacji o użytych regułach i podanym wyniku zwraca informacje o błędach. None wskazuje na poprawność wyprowadzenia wniosku z reguły.
    Konceptualnie przypomina zbiory Hintikki bez reguły o niesprzeczności.
    """
    premiss = rule.get_branch()[rule.decisions['sentenceID']]
    entailed = RULES[rule.rule].strict(premiss, **rule.context)
    if entailed and conclusion in sum(entailed, ()):
        return None
    else:
        return UserMistake('wrong rule', f"'{rule.rule}' can't be used on '{premiss.getReadable()}'", {'rule':rule.rule, 'premiss':premiss})
    

def use_rule(name: str, branch: list[Sentence], used: utils.History, context: dict[str, tp.Any], decisions: dict[str, tp.Any]) -> tuple[utils.SentenceTupleStructure, utils.HistoryTupleStructure, dict[str, tp.Any]]:
    """
    Używa określonej reguły na podanej gałęzi.
    Więcej: https://www.notion.so/szymanski/Gniazda-w-Larchu-637a500c36304ee28d3abe11297bfdb2#98e96d34d3c54077834bc0384020ff38

    :param name: Nazwa używanej reguły, listę można uzyskać z pomocą Formal.get_rules_docs()
    :type name: str
    :param branch: Lista zdań w gałęzi, na której została użyta reguła
    :type branch: list[Sentence]
    :param used: Obiekt historii przechowujący informacje o już rozłożonych zdaniach
    :type used: utils.History
    :param context: kontekst wymagany do zastosowania reguły, listę można uzyskać z pomocą Formal.get_needed_context(rule)
        Kontekst reguł: https://www.notion.so/szymanski/Zarz-dzanie-kontekstem-regu-2a5abea2a1bc492e8fa3f8b1c046ad3a
    :type context: dict[str, tp.Any]
    :param decisions: Zbiór podjętych przez program decyzji (mogą być czymkolwiek), które nie wynikają deterministycznie z przesłanek, używane jest do odtworzenia reguł przy wczytywaniu dowodu.
    :type decisions: dict[str, Any]
    :return: Struktura krotek, reprezentująca wynik reguły oraz strukturę reprezentującą operacje do wykonania na zbiorze zamknięcia.
        Struktury krotek: https://www.notion.so/szymanski/Reprezentacja-dowod-w-w-Larchu-cd36457b437e456a87b4e0c2c2e38bd5#014dccf44246407380c4e30b2ea598a9
        Zamykanie gałęzi: https://www.notion.so/szymanski/Zamykanie-ga-zi-53249279f1884ab4b6f58bbd6346ec8d
    :rtype: tuple[tp.Union[tuple[tuple[Sentence]], None], tp.Union[tuple[tuple[tp.Union[int, Callable, Sentence]]], None]]
    """
    rule = RULES[name]

    _, (start_left, start_right) = branch[-1].getComponents(PRECEDENCE)
    start_left, start_right = start_left or Sentence([], None), start_right or Sentence([], None)

    history = None
    if name == "left imp":
        if start_right in used:
            raise RaisedUserMistake('loop-detection', "Operation prohibited by loop detection algorithm")
        else:
            history = [[start_right], [0]]
    elif name == 'left or':
        history = [[-1], [-1]]
    elif name == 'right imp':
        l = utils.strip_around(start_right, "imp", False)
        if l is None:
            raise RaisedUserMistake('wrong rule', 'You\'ve used a wrong rule')
        elif is_sequent(start_left, l[0][0]):
            history = [[0]]
        else:
            history = [[-1]]

    conc = rule.naive(branch, *context.values())

    # Outcome return
    if conc:
        # History length multiplication
        if not history:
            history = [[0]]*len(conc)
        return conc, history, {'sentenceID':len(branch)-1}
    else:
        raise RaisedUserMistake('wrong rule', 'You\'ve used a wrong rule')