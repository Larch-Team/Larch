"""
Zastępstwo zeroth_order_logic z zaimplementowanym checkerem opartych na intuicjach zbiorów Hintikki oraz prostym solverem. Korzysta z nowo wprowadzonych drzew regułowych. Reguły działają na bazie tablic Smullyana. Po raz pierwszy zaimplementowany został system naiwny.
"""
import typing as tp
from collections import namedtuple

from history import History
from proof import Proof
from rule import Rule, SentenceID
from sentence import Sentence
from tree import ProofNode
from usedrule import UsedRule

import Formal.__utils__ as utils
from Formal.__template__ import check_closure

SOCKET = 'Formal'
VERSION = '0.2.0'

PRECEDENCE = {
    'and': 3,
    'or': 3,
    'imp': 2,
    'not': 4
}


def get_operator_precedence() -> dict[str, int]:
    """Zwraca siłę wiązania danych spójników, im wyższa, tym mocniej wiąże (negacja ma najwyższą przykładowo)"""
    return PRECEDENCE


def prepare_for_proving(statement: utils.Sentence) -> utils.Sentence:
    """Przygotowuje zdanie do dowodzenia - czyszczenie, dodawanie elementów"""
    return utils.add_prefix(statement, 'not', "~")


# SYNTAX CHECKING

def synchk_transcribe(sentence):
    s = []
    for el in sentence:
        if el in ['(', ')']:
            s.append(el)
        else:
            elem = el.split('_')
            if elem[0] == 'sentvar':
                s.append("s")
            elif elem[0] == 'not':
                s.append("1")
            elif elem[0] in ('and', 'or', 'imp'):
                s.append("2")
    return "".join(s)


def special_replace(string, old, new, index_list):
    while string.find(old) != -1:
        a = string.find(old)
        string = string.replace(old, new, 1)
        del index_list[a:a+len(old)]
        index_list.insert(a, None)
    return string, index_list


def reduce_(sentence):
    prev_sentence = ''
    sentence = synchk_transcribe(sentence)
    indexes = list(range(len(sentence)))
    while prev_sentence != sentence:
        prev_sentence = sentence
        for to_replace in ('1s', 's2s', '(s)'):
            sentence, indexes = special_replace(
                sentence, to_replace, "s", indexes)
    return sentence, indexes


def find_all(a_str, sub):
    start = 0
    while True:
        start = a_str.find(sub, start)
        if start == -1:
            return
        yield start
        start += len(sub)


def check_syntax(sentence: utils.Sentence) -> tp.Union[str, None]:
    """Sprawdza poprawność zapisu tokenizowanego zdania, zwraca informacje o błędach w formule"""
    reduced, indexes = reduce_(sentence)
    if reduced == 's':
        # ok
        return None
    if 's' not in reduced:
        return 'Zdanie nie zawiera żadnych zmiennych'

    if 'ss' in reduced:
        return 'W zdaniu znajdują się dwie zmienne lub formuły niepołączone spójnikiem'

    if '(' in reduced:
        errors = find_all(reduced, '(')
        for er in errors:
            return f'Otwarcie nawiasu na pozycji {indexes[er]+1} nie ma zamknięcia'

    if ')' in reduced:
        errors = find_all(reduced, '(')
        for er in errors:
            return f'Zamknięcie nawiasu na pozycji {indexes[er]+1} nie ma otwarcia'

    if 's2' in reduced:
        errors = find_all(reduced, 's2')
        for er in errors:
            return f'Spójnik dwuargumentowy na pozycji {indexes[er]+2} nie ma prawego argumentu'

    if '2s' in reduced:
        errors = find_all(reduced, '2s')
        for er in errors:
            return f'Spójnik dwuargumentowy na pozycji {indexes[er]+1} nie ma lewego argumentu'
    raise Exception('Zdanie nie jest poprawne')


# RULES

RULES = {
    'double not': utils.Rule(
        name='double not',
        symbolic="~~A / A",
        docs="Usuwanie podwójnej negacji. Wymaga wskazania zdania w gałęzi.",
        reusable=False
    ),
    'true and': utils.Smullyan(
        name='true and',
        symbolic="A and B / A; B",
        docs="Rozkładanie prawdziwej koniunkcji. Wymaga wskazania zdania w gałęzi oraz rozkładanego spójnika.",
        reusable=False
    ),
    'false or': utils.Smullyan(
        name='false or',
        symbolic="~(A or B) / ~A; ~B",
        docs="Rozkładanie fałszywej alternatywy. Wymaga wskazania zdania w gałęzi oraz rozkładanego spójnika.",
        reusable=False
    ),
    'false imp': utils.Smullyan(
        name='false imp',
        symbolic="~(A -> B) / A; ~B",
        docs="Rozkładanie fałszywej implikacji. Wymaga wskazania zdania w gałęzi oraz rozkładanego spójnika.",
        reusable=False
    ),
    'true or': utils.Smullyan(
        name='true or',
        symbolic="(A or B) / A | B",
        docs="Rozkładanie prawdziwej alternatywy. Wymaga wskazania zdania w gałęzi oraz rozkładanego spójnika.",
        reusable=False
    ),
    'false and': utils.Smullyan(
        name='false and',
        symbolic="~(A and B) / ~A | ~B",
        docs="Rozkładanie fałszywej koniunkcji. Wymaga wskazania zdania w gałęzi oraz rozkładanego spójnika.",
        reusable=False
    ),
    'true imp': utils.Smullyan(
        name='true imp',
        symbolic="(A -> B) / ~A | B",
        docs="Rozkładanie prawdziwej implikacji. Wymaga wskazania zdania w gałęzi oraz rozkładanego spójnika.",
        reusable=False
    )
}

double_not = RULES['double not']

ROOT_RULE = RULES['double not']
RULES['double not'].children = (RULES['true and'],)
RULES['true and'].children = (RULES['false or'],)
RULES['false or'].children = (RULES['false imp'],)
RULES['false imp'].children = (RULES['true or'],)
RULES['true or'].children = (RULES['false and'],)
RULES['false and'].children = (RULES['true imp'],)


@double_not.setStrict
def strict_doublenot(sentence: Sentence):
    return utils.reduce_prefix(utils.reduce_prefix(utils.empty_creator(sentence), 'not'), 'not')


@double_not.setNaive
def naive_doublenot(branch: list[Sentence], sentenceID: SentenceID):
    return utils.reduce_prefix(utils.reduce_prefix(utils.empty_creator(branch[sentenceID]), 'not'), 'not')


# CHECKER


# def checker(rule: UsedRule, conclusion: Sentence) -> bool:
#     # sourcery skip: merge-duplicate-blocks
#     premiss = rule.get_premisses()[0]
#     connective, use_result = premiss.getComponents()
#     if connective.startswith('not'):
#         # zastosowanie reguły dla prawdziwości na zanegowanej formule
#         if rule.rule.startswith('true'):
#             return False
#         connective, use_result = use_result[1].getComponents()
#     # zastosowanie reguły dla fałszywości na niezanegowanej formule
#     elif rule.rule.startswith('false'):
#         return False

#     # Zastosowanie reguły dla złego spójnika
#     if not connective.startswith(rule.rule.split()[1]):
#         return False
#     # Sprawdzenie, czy reguły zastosowano na poprawnej instancji spójnika
#     else:
#         return conclusion.getNonNegated() in {i.getNonNegated() for i in use_result}


def checker(rule: UsedRule, conclusion: Sentence) -> tp.Union[str, None]:
    """
    Na podstawie informacji o użytych regułach i podanym wyniku zwraca informacje o błędach. None wskazuje na poprawność wyprowadzenia wniosku z reguły.
    Konceptualnie przypomina zbiory Hintikki bez reguły o niesprzeczności.
    """
    premiss = rule.get_premisses()['sentenceID']  # Istnieje tylko jedna
    entailed = RULES[rule.rule].strict(premiss)
    if not entailed:
        return f"'{rule.rule}' can't be used on '{premiss.getReadable()}'"
    elif conclusion in sum(entailed, ()) and find_rule(premiss) == rule.rule:
        return None
    else:
        return f"Check which connective is the main one in '{premiss.getReadable()}'"


# SOLVER


SignedSentence = namedtuple('SignedSentence', ['sentence', 'branch', 'id'])


def find_rule(sentence: Sentence) -> str:
    main, other = sentence.getComponents()
    if main is None:
        return None
    if main.startswith('not_'):
        negated = 'false'
        main, _ = other[1].getComponents()
    else:
        negated = 'true'

    if main.startswith('not_'):
        return 'double not'
    else:
        return f"{negated} {main.split('_')[0]}"


def group_by_rules(proof: Proof) -> dict[str, list[SignedSentence]]:

    containers = {i: [] for i in RULES.keys()}
    for leaf in proof.nodes.getleaves():
        branch, closed = leaf.getbranch_sentences()
        if closed:
            continue

        for num, sentence in enumerate(branch):
            if sentence in leaf.history:
                continue

            if (rule := find_rule(sentence)) is not None:
                containers[rule].append(
                    SignedSentence(sentence, leaf.branch, num))
    return containers


def append_by_rules(containers: dict[str, list[SignedSentence]], nodes: tp.Iterable[ProofNode]) -> dict[str, list[SignedSentence]]:

    for node in nodes:
        num = len(node.path)
        
        if (rule := find_rule(node.sentence)) is not None:
            containers[rule].append(
                SignedSentence(node.sentence, node.branch, num))
    return containers


def use_strict(proof: Proof, rule: Rule, sentence: SignedSentence) -> tuple[ProofNode]:
    old = proof.nodes.getleaf(sentence.branch)

    # Rule usage
    fin = rule.strict(sentence.sentence)
    assert fin

    layer = proof.append(fin, sentence.branch)
    ProofNode.insert_history(
        ([[0]] if rule.reusable else [[sentence]]), old.children)

    context = {
        'sentenceID': sentence.id,
        'tokenID': sentence.sentence
    }

    proof.metadata['usedrules'].append(
        UsedRule(layer, sentence.branch, rule, proof, context=context, auto=True))
    return old.children


def _pop_default(l: list, index: int = -1, default: tp.Any = None) -> tp.Any:
    try:
        return l.pop(index)
    except IndexError:
        return default


def propagate_rule(proof: Proof, rule: Rule, containers: dict[str, list[SignedSentence]]) -> dict[str, list[SignedSentence]]:
    if not containers[rule.name]:
        return containers
    closed = []
    while (sentence := _pop_default(containers[rule.name])):
        if sentence.branch in closed:
            continue
        new = use_strict(proof, rule, sentence)
        for nodes in new:
            if proof.deal_closure_func(check_closure, new.branch):
                closed.append(new.branch)
        containers = append_by_rules(containers, new)
    return {i:[k for k in j if not k.branch in closed] for i,j in containers.items()}


def _solver(proof: Proof, rule: Rule, containers: dict[str, list[SignedSentence]]) -> bool:
    start_used = proof.metadata['usedrules'][:]
    start_layer = start_used[-1].layer
    containers = propagate_rule(proof, rule)
    if proof.nodes.is_closed():
        return True
    
    while any(containers[i.name] for i in rule.ancestors):
        for past_rule in rule.ancestors:
            containers = propagate_rule(proof, rule)
    if proof.nodes.is_closed():
        return True
    
    for child in Rule.children:
        if _solver(proof, child, containers[:]):
            return True
        
    proof.metadata['usedrules'] = start_used
    proof.nodes.pop(start_layer+1)
    return False
                

def solver(proof: Proof) -> bool:
    containers = group_by_rules(proof)
    return _solver(proof, ROOT_RULE, containers)


def check_closure(branch: list[utils.Sentence], used: History) -> tp.Union[None, tuple[utils.close.Close, str]]:
    """Sprawdza możliwość zamknięcia gałęzi, zwraca obiekty zamknięcia oraz komunikat do wyświetlenia""" 
    for num1, statement_1 in enumerate(branch):
        for num2, statement_2 in enumerate(branch):
            if statement_1[0].startswith('not') and not statement_2[0].startswith('not'):
                negated, statement = statement_1, statement_2
            elif statement_2[0].startswith('not') and not statement_1[0].startswith('not'):
                negated, statement = statement_2, statement_1
            else:
                continue

            if utils.reduce_prefix(negated, 'not') == statement:
                return utils.close.Contradiction(sentenceID1=num1+1, sentenceID2=num2+1), "Sentences contradict. The branch was closed."

    if all(i in used or i.isLiteral() for i in branch):
        return utils.close.Emptiness, "Nothing else to be done, branch was closed."
    return None


def get_used_types() -> tuple[str]:
    return ('and', 'or', 'imp', 'not', 'sentvar')


def get_rules_docs() -> dict[str, str]:
    """Zwraca reguły rachunku z opisem"""
    return {rule.name: rule.__doc__ for rule in RULES.values()}


def get_needed_context(rule_name: str) -> tuple[utils.ContextDef]:
    """Zwraca informacje o wymaganym przez daną regułę kontekście w formie obiektów ContextDef"""
    return RULES[rule_name].context if RULES.get(rule_name) else None


def use_rule(name: str, branch: list[utils.Sentence], used: utils.History, context: dict[str, tp.Any], decisions: dict[str, tp.Any]) -> tuple[utils.SentenceTupleStructure, utils.HistoryTupleStructure, dict[str, tp.Any]]:
    """
    Używa określonej reguły na podanej gałęzi.
    Więcej: https://www.notion.so/szymanski/Gniazda-w-Larchu-637a500c36304ee28d3abe11297bfdb2#98e96d34d3c54077834bc0384020ff38

    :param name: Nazwa używanej reguły, listę można uzyskać z pomocą Formal.get_rules_docs()
    :type name: str
    :param branch: Lista zdań w gałęzi, na której została użyta reguła
    :type branch: list[utils.Sentence]
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
    :rtype: tuple[tp.Union[tuple[tuple[utils.Sentence]], None], tp.Union[tuple[tuple[tp.Union[int, Callable, utils.Sentence]]], None]]
    """
    rule = RULES[name]
    sentenceID = context['sentenceID']

    if sentenceID < 0 or sentenceID >= len(branch):
        raise utils.FormalError("No such sentence")
    sentence = branch[sentenceID]

    if not rule.reusable and sentence in used:  # Used sentence filtering
        raise utils.FormalError(
            "This sentence was already used in a non-reusable rule")

    # Rule usage
    important_context = {i: j for i, j in context.items() if i in {
        i.variable for i in rule.context}}
    fin = rule.naive(branch, **important_context)
    if fin:
        return fin, len(fin)*([[0]] if rule.reusable else [[sentence]]), None
    else:
        return None, None, None
