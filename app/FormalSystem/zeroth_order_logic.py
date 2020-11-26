import typing as tp
import FormalSystem as utils

SOCKET = 'FormalSystem'
VERSION = '0.0.1'


# Rule definition


USED_TYPES = ('and', 'or', 'imp', 'not', 'sentvar')
PRECEDENCE = {
    'and':3,
    'or':3,
    'imp':2,
}

def red_neg(x):
    return utils.reduce_prefix(x, 'not', ('not'))

RULES = {
    'true and': utils.Rule(
        symbolic="A and B / A; B",
        docs="Needs sentence ID",
        func=lambda x: utils.strip_around(x, 'and', False, PRECEDENCE),
        reusable=True
    ),
    'false and': utils.Rule(
        symbolic="~(A and B) / ~A | ~B",
        docs="Needs sentence ID",
        func=lambda x: utils.add_prefix(utils.strip_around(
            red_neg(x), 'and', True, PRECEDENCE), 'not', '~'),
        reusable=False
    ),
    'false or': utils.Rule(
        symbolic="~(A or B) / ~A; ~B",
        docs="Needs sentence ID",
        func=lambda x: utils.add_prefix(utils.strip_around(
            red_neg(x), 'or', False, PRECEDENCE), 'not', '~'),
        reusable=True
    ),
    'true or': utils.Rule(
        symbolic="(A or B) / A | B",
        docs="Needs sentence ID",
        func=lambda x: utils.strip_around(x, 'or', True, PRECEDENCE),
        reusable=False
    ),
    'false imp': utils.Rule(
        symbolic="~(A -> B) / A; ~B",
        docs="Needs sentence ID",
        func=lambda x: utils.select(utils.strip_around(red_neg(x),'imp', False, PRECEDENCE), ((False, True),), lambda y: utils.add_prefix(y, 'not', '~')),
        reusable=True
    ),
    'true imp': utils.Rule(
        symbolic="(A -> B) / ~A | B",
        docs="Needs sentence ID",
        func=lambda x: utils.select(utils.strip_around(x, 'imp', True, PRECEDENCE), ((True,), (False,)), lambda y: utils.add_prefix(y, 'not', '~')),
        reusable=False
    ),
    'double not': utils.Rule(
        symbolic="~~A / A",
        docs="Needs sentence ID",
        func=lambda x: utils.reduce_prefix(
            utils.reduce_prefix(utils.empty_creator(x), 'not', ('not')), 'not', ('not')),
        reusable=True
    )
}


# __template__


@utils.cleaned
def prepare_for_proving(statement: utils.Sentence) -> str:
    """Cleaning the sentence"""
    return statement


def check_contradict(statement_1: utils.Sentence, statement_2: utils.Sentence) -> bool:
    """Checks whether statements collide with eachother"""
    if statement_1[0].startswith('not') and not statement_2[0].startswith('not'):
        negated, statement = statement_1, statement_2
    elif statement_2[0].startswith('not') and not statement_1[0].startswith('not'):
        negated, statement = statement_2, statement_1
    else:
        return False
    return utils.reduce_brackets(negated[1:]) == statement


def check_syntax(sentence: utils.Sentence) -> tp.Union[str, None]:
    """True if sentence's syntax is correct; Doesn't check brackets"""
    return None
    # TODO: napisać check oparty na redukcji ze sprawdzaniem nawiasów i sprawdzanie czy w każdym występuje "_"
    # tested = "".join(tokenized_statement).replace("(", "").replace(")", "")
    # pattern = re.compile(r'(<not_.{1,3}>)?(<sentvar_\w>)<.{2,3}_.{1,3}>(<not_.{1,3}>)?(<sentvar_\w>)')
    # if pattern.match(tested):
    #     return None
    # else:
    #     after = pattern.sub(tested, '<sentvar_X>')
    #     if after==tested:
    #         return "Wrong structure"
    #     else:
    #         tested=after[:]


def check_rule_reuse(rule_name: str) -> bool:
    """Checks whether the rule can be reused on one statement in one branch"""
    return RULES[rule_name].reusable


def get_rules() -> dict[str, str]:
    """Returns the names and documentation of the rules"""
    rule_dict = dict()
    for name, rule in RULES.items():
        rule_dict[name] = "\n".join((rule.symbolic, rule.docs))
    return rule_dict


def get_used_types() -> tuple[str]:
    return USED_TYPES


def use_rule(name: str, branch: list[utils.Sentence], context: dict[str,tp.Any]) -> tuple[tp.Union[tuple[tuple[utils.Sentence]], None], int]:
    """Uses a rule of the given name on the provided branch.
        Context allows to give the FormalSystem additional arguments. 
        This system only uses sentenceID

    :param name: Rule name
    :type name: str
    :param branch: List of sentences in a branch
    :type branch: list[utils.Sentence]
    :param context: Additional arguments (here it's only sentenceID)
    :type context: dict[str,tp.Any]
    :return: Generated tuple structure with the sentences and sentence ID
    :rtype: tuple[tp.Union[tuple[tuple[utils.Sentence]], None], int]
    """
    rule = RULES[name]
    statement_ID = context['sentenceID']

    # Sentence getting
    if statement_ID < 0 or statement_ID > len(branch):
            raise utils.FormalSystemError("No such sentence")
    tokenized_statement = branch[statement_ID]

    if not tokenized_statement: # Used sentence filtering
        raise utils.FormalSystemError("This sentence was already used in a non-reusable rule")

    # Rule usage
    fin = rule.func(tokenized_statement)
    if fin:
        return fin, statement_ID
    else:
        return None, -1


def get_needed_context(rule_name: str) -> tuple[utils.ContextDef]:
    """Returns needed arguments for the given rule"""
    return tuple([utils.ContextDef(variable='sentenceID', official='Sentence Number', docs='', type_='sentenceID')])