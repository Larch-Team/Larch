import typing as tp
import FormalSystem as utils

SOCKET = 'FormalSystem'
VERSION = '0.0.1'


USED_TYPES = ('and', 'or', 'imp', 'sentvar', 'sep', 'turnstile','falsum')
PRECEDENCE = {
    'and': 4,
    'or': 4,
    'imp': 3,
    'sep': 2,
    'turnstile': 1
}


def is_sequent(l, s) -> bool:
    buffor = []
    for i in l:
        if i.startswith('sep_'):
            if buffor == s:
                return True
            else:
                buffor = []
        else:
            buffor.append(i)
    if buffor == s:
        return True
    return False


def get_part(sentence: utils.Sentence, split_type: str, sent_num: int):
    """
    Returns n-th part of the sentence (split_types is the type of separator)

    Changes the sentence!!
    """
    split_count = 0
    start_split = 0
    for s in sentence:
        if s.startswith(f"{split_type}_"):
            split_count += 1
        if split_count == sent_num:
            break
        start_split += 1

    if len(sentence) <= start_split or split_count<sent_num:
        raise IndexError("sent_num is too big")

    part = []
    if split_count>0:
        sentence.pop(start_split)
    
    while start_split<len(sentence) and not sentence[start_split].startswith(f"{split_type}_"):
        part.append(sentence.pop(start_split))

    if len(sentence)>0 and split_count == 0:
        sentence.pop(start_split)
    return part


def merge_tupstruct(left: tuple[tuple[str]], right: tuple[tuple[str]], glue: str):
    """
    Merges two tuple structures into one
    """
    if isinstance(left, tuple) and isinstance(left, tuple):
        assert len(left) == len(right), "Tuples not of equal length"
        end = []
        for l, r in zip(left, right):
            end.append(merge_tupstruct(l, r, glue))
        return tuple(end)
    elif isinstance(left, list) and isinstance(left, list):
        return left + [glue] + right
    else:
        # Bug reporting
        l_correct = (isinstance(left, list) or isinstance(left, tuple))
        r_correct = (isinstance(right, list) or isinstance(right, tuple))
        if l_correct and r_correct:
            raise AssertionError("Tuples not of equal depth")
        else:
            raise AssertionError((l_correct*"left")+(l_correct*r_correct *' and ')+(r_correct*"right") + "tuple is messed up")


def sep(part: utils.Sentence = None) -> list[str]:
    if part is None or (len(part)>0 and not part[0].startswith('sep_;')):
        return ['sep_;']
    else:
        return []


# Rule definition


def rule_left_and(left: utils.Sentence, right: utils.Sentence, num: int):
    """ A,B,... => ...
        ______________
        A&B,... => ...
    """
    try:
        conj = get_part(left, 'sep', num-1)
    except IndexError:
        return (None, None)
    
    split = utils.strip_around(conj, 'and', False, PRECEDENCE)
    if split is None or split[0] is None:
        return (None, None)
    split = split[0]
    return ((split[0]+sep()+split[1]+sep(left)+left,),), ((right,),)


def rule_right_and(left: utils.Sentence, right: utils.Sentence):
    """ ... => A      ... => B
        __________________________
        ... => A&B
    """
    conj = get_part(right, 'sep', 0)
    if conj is None:
        return (None, None)

    split = utils.strip_around(conj, 'and', False, PRECEDENCE)
    if split is None or split[0] is None:
        return (None, None)
    split = split[0]
    return ((left,),(left,),), ((split[0],),(split[1],),)

def rule_left_or(left: utils.Sentence, right: utils.Sentence, num: int):
    """ A,... => ...  B,... => ...
        __________________________
        AvB,... => ...
    """
    try:
        conj = get_part(left, 'sep', num-1)
    except IndexError:
        return (None, None)
    
    split = utils.strip_around(conj, 'or', False, PRECEDENCE)
    if split is None or split[0] is None:
        return (None, None)
    split = split[0]
    return ((split[0]+sep(left)+left,),(split[1]+sep(left)+left,),), ((right,),(right,),)


def rule_right_or(left: utils.Sentence, right: utils.Sentence, side: str):
    """ ... => (A,B)[side]
        ______________
        ... => AvB
    """
    if not right or side not in ('l', 'r','find'):
        return (None, None)
    
    subsent = get_part(right, 'sep', 0)
    split = utils.strip_around(subsent, 'or', False, PRECEDENCE)
    if split is None or split[0] is None:
        return (None, None)
    left_split, right_split = split[0]
    
    if side=='l':
        return ((left,),), ((left_split,),)
    elif side=='r':
        return ((left,),), ((right_split,),)
    else:
        if is_sequent(left, left_split):
            return ((left,),), ((left_split,),)
        elif is_sequent(left, right_split):
            return ((left,),), ((right_split,),)
        else:
            # Default case
            return ((left,),), ((max(split[0], key=len),),)



def rule_left_imp(left: utils.Sentence, right: utils.Sentence, num: int):
    """ A -> B, ... => A    B,... => ...
        ________________________________
        A -> B,... => ...
    """
    try:
        conj = get_part(left, 'sep', num-1)
    except IndexError:
        return (None, None)
    
    split = utils.strip_around(conj, 'imp', False, PRECEDENCE)
    if split is None or split[0] is None:
        return (None, None)
    split = split[0]
    return ((conj+sep(left)+left,),(split[1]+sep(left)+left,),), ((split[0],),(right,),)


def rule_right_imp(left: utils.Sentence, right: utils.Sentence):
    """ ..., A => B
        ______________
        ... => A -> B
    """
    try:
        conj = get_part(right, 'sep', 0)
    except IndexError:
        return (None, None)
    
    split = utils.strip_around(conj, 'imp', False, PRECEDENCE)
    if split is None or split[0] is None:
        return (None, None)
    split = split[0]
    return ((split[0]+sep(left)+left,),), ((split[1],),)

def rule_left_strong(left: utils.Sentence, right: utils.Sentence, num: int):
    """ ..., A, A => ...
        ________________
        ..., A => ...
    """
    try:
        conj = get_part(left, 'sep', num-1)
    except IndexError:
        return (None, None)
    
    return ((conj+sep()+conj+sep(left)+left,),), ((right,),)

def rule_left_weak(left: utils.Sentence, right: utils.Sentence, num: int):
    """ ... => ...
        ______________
        ..., A => ...
    """
    try:
        conj = get_part(left, 'sep', num-1)
    except IndexError:
        return (None, None)
    
    return ((left,),), ((right,),)

RULES = {
    'left and': utils.Rule(
        symbolic="",
        docs="",
        func=rule_left_and,
        reusable=None, # Not needed
        context=[utils.ContextDef(
            variable='partID',
            official='Subsentence number',
            docs='',
            type_=int
        )]
    ),
    'left or': utils.Rule(
        symbolic="",
        docs="",
        func=rule_left_or,
        reusable=None, # Not needed
        context=[utils.ContextDef(
            variable='partID',
            official='Subsentence number',
            docs='',
            type_=int
        )]
    ),
    'right and': utils.Rule(
        symbolic="",
        docs="",
        func=rule_right_and,
        reusable=None, # Not needed
        context=[]
    ),
    'right or': utils.Rule(
        symbolic="",
        docs="",
        func=rule_right_or,
        reusable=None, # Not needed
        context=[
        utils.ContextDef(
            variable='conn_side',
            official='Side of the or operation',
            docs='l/r/find; `find` option searches for the best possible fit',
            type_=str
        )]
    ),
    'left imp': utils.Rule(
        symbolic="",
        docs="",
        func=rule_left_imp,
        reusable=None, # Not needed
        context=[utils.ContextDef(
            variable='partID',
            official='Subsentence number',
            docs='',
            type_=int
        )]
    ),
    'right imp': utils.Rule(
        symbolic="",
        docs="",
        func=rule_right_imp,
        reusable=None, # Not needed
        context=[]
    ),
    'left weak': utils.Rule(
        symbolic="",
        docs="",
        func=rule_left_weak,
        reusable=None, # Not needed
        context=[utils.ContextDef(
            variable='partID',
            official='Subsentence number',
            docs='',
            type_=int
        )]
    ),
    'left strong': utils.Rule(
        symbolic="",
        docs="",
        func=rule_left_strong,
        reusable=None, # Not needed
        context=[utils.ContextDef(
            variable='partID',
            official='Subsentence number',
            docs='',
            type_=int
        )]
    ),
}

# __template__


def prepare_for_proving(statement: utils.Sentence) -> utils.Sentence:
    if not 'turnstile_=>' in statement:
        return ['turnstile_=>']+statement
    else:
        return statement


def check_contradict(branch: list[utils.Sentence], used: set[tuple[str]]) -> tp.Union[None, tuple[int, str, str]]:
    left, right = utils.strip_around(branch[-1], "turnstile", False, PRECEDENCE)[0]
    seps = sum((i.startswith('sep_') for i in left), 1)

    # Right part verification
    empty = len(right)==1

    # Left part verification
    if len(left)==0:
        return None
    for i in range(0, seps):
        f = get_part(left[:], 'sep', i)

        # F, ... => ...
        if len(f)==1 and f[0].startswith("falsum_"):
            return 1, f"Falsum", f"Falsum found on the left"

        # p, ... => p
        if f==right:
            return 1, f"Ax", f"Sequent on the right corresponds with a sequent on the left"

        # Detect finish
        empty &= not any((any((j.startswith(i) for j in f)) for i in ('and_', 'or_', 'imp_')))

    if empty:
        return 0, "", "Nothing more can be done with this branch, so it was closed."


def check_syntax(tokenized_statement: utils.Sentence) -> tp.Union[str, None]:
    """Should return string description of the problem in syntax"""
    return True


def get_rules() -> dict[str, str]:
    """Returns the names and documentation of the rules"""
    rule_dict = dict()
    for name, rule in RULES.items():
        rule_dict[name] = "\n".join((rule.symbolic, rule.docs))
    return rule_dict


def get_needed_context(rule_name: str) -> tuple[utils.ContextDef]:
    """Returns needed arguments for the given rule"""
    if (rule := RULES.get(rule_name, None)):
        return tuple(rule.context)
    else:
        return None


def get_used_types() -> tuple[str]:
    return USED_TYPES


def use_rule(name: str, branch: list[utils.Sentence], used: set[utils.Sentence], context: dict[str, tp.Any]) -> tuple[tp.Union[tuple[tuple[utils.Sentence]], None], int]:
    """Uses a rule of the given name on the provided branch.
        Context allows to give the FormalSystem additional arguments. 
        Use `self.access('FormalSystem').get_needed_context(rule)` to check for needed context

    :param name: Rule name
    :type name: str
    :param branch: List of sentences in a branch
    :type branch: list[utils.Sentence]
    :param context: Additional arguments
    :param used: Set of sentences that were already used
    :type used: set[utils.Sentence]
    :type context: dict[str,tp.Any]
    :return: Generated tuple structure with the sentences and sentence ID
    :rtype: tuple[tp.Union[tuple[tuple[utils.Sentence]], None], int]
    """
    rule = RULES[name]

    start = utils.strip_around(branch[-1], "turnstile", False, PRECEDENCE)
    start_left, start_right = start[0]
    
    # Check sequent number
    if context.get('partID', -1) > sum(i.startswith('sep') for i in start_left)+1:
        raise utils.FormalSystemError("Sequent number is too big")

    # Loop detection
    history = None
    if name == "left imp":
        if tuple(start_right) in used:
            raise utils.FormalSystemError("Operation prohibited by loop detection algorithm")
        else:
            history = [start_right, 0]

    # Rule usage
    left, right = rule.func(start_left[:], start_right[:], *context.values())

    # Loop detection
    if not (left is None or right is None):
        if name == 'left or':
            history = [-1, -1]
        elif name == 'right imp':
            l = utils.strip_around(start_right, "imp", False, PRECEDENCE)[0][0]
            if is_sequent(start_left, l):
                history = [0]
            else:
                history = [-1]

    # Outcome return
    if not (left is None or right is None):
        # History length multiplication
        if not history:
            history = [0]*len(left)
        return merge_tupstruct(left, right, "turnstile_=>"), history
    else:
        return None, None
