
from typing import Callable
from exceptions import RaisedUserMistake
import plugins.Formal.__utils__ as utils

from sentence import Sentence
from libs import sep, pop_part
from rule import Rule, SentenceTupleStructure, TokenID

PRECEDENCE = {
    'and': 4,
    'or': 4,
    'imp': 3,
    'sep': 2,
    'turnstile': 1
}

def make_left(rule: Rule):
    def _make_left(func: Callable[[Sentence, Sentence, TokenID], SentenceTupleStructure]):
        
        @rule.setNaive
        def naive(branch: list[Sentence], tokenID: TokenID):
            t, (l, r) = branch[-1].getComponents()
            l, r = l or Sentence([], None), r or Sentence([], None)
            assert t.startswith('turnstile')
            left, right = func(l, r, tokenID)
            if left is None or right is None:
                raise RaisedUserMistake('wrong rule', 'You\'ve used a wrong rule')
            return utils.merge_tupstruct(left, right, "turnstile_=>")
        
        @rule.setStrict
        def strict(sentence: Sentence, tokenID: TokenID):
            t, (l, r) = sentence.getComponents()
            l, r = l or Sentence([], None), r or Sentence([], None)
            assert t.startswith('turnstile')
            left, right = func(l, r, tokenID)
            return utils.merge_tupstruct(left, right, "turnstile_=>")
        
    return _make_left
        
def make_right(rule: Rule):
    def _make_right(func: Callable[[Sentence, Sentence], SentenceTupleStructure]):
        
        @rule.setNaive
        def naive(branch: list[Sentence]):
            t, (l, r) = branch[-1].getComponents()
            l, r = l or Sentence([], None), r or Sentence([], None)
            
            assert t.startswith('turnstile')
            left, right = func(l, r)
            if left is None or right is None:
                raise RaisedUserMistake('wrong rule', 'You\'ve used a wrong rule')
            return utils.merge_tupstruct(left, right, "turnstile_=>")
        
        @rule.setStrict
        def strict(sentence: Sentence):
            t, (l, r) = sentence.getComponents()
            l, r = l or Sentence([], None), r or Sentence([], None)
            assert t.startswith('turnstile')
            left, right = func(l, r)
            return utils.merge_tupstruct(left, right, "turnstile_=>")
    
    return _make_right
          


# Rule definition


left_and = utils.Rule('left and',
        symbolic="A&B, ... => ... // A, B, ... => ...",
        docs="Rozkładanie koniunkcji po lewej stronie sekwentu",
        reusable=None # Not needed
)

@make_left(rule=left_and)
def func_left_and(left: utils.Sentence, right: utils.Sentence, num: int):
    """ A,B,... => ...
        ______________
        A&B,... => ...
    """
    conj, rest = pop_part(left, num)
    if conj is None:
        return (None, None)
    
    split = utils.strip_around(conj, 'and', False)
    if split is None or split[0] is None:
        return (None, None)
    split = split[0]
    return ((split[0]+sep()+split[1]+sep(rest)+rest,),), ((right,),)


right_and = utils.Rule('right and',
        symbolic="... => A & B // ... => A | ... => B",
        docs="Rozkładanie koniunkcji po prawej stronie sekwentu",
        reusable=None # Not needed
)

@make_right(rule=right_and)
def func_right_and(left: utils.Sentence, right: utils.Sentence):
    """ ... => A      ... => B
        __________________________
        ... => A&B
    """

    split = utils.strip_around(right, 'and', False)
    if split is None or split[0] is None:
        return (None, None)
    split = split[0]
    return ((left,),(left,),), ((split[0],),(split[1],),)


left_or = utils.Rule('left or',
        symbolic="A v B, ... => ... // A, B, ... => ...",
        docs="Rozkładanie alternatywy po lewej stronie sekwentu",
        reusable=None # Not needed
)

@make_left(rule=left_or)
def func_left_or(left: utils.Sentence, right: utils.Sentence, num: int):
    """ A,... => ...  B,... => ...
        __________________________
        AvB,... => ...
    """
    conj, rest = pop_part(left, num)
    if conj is None:
        return (None, None)
    
    split = utils.strip_around(conj, 'or', False)
    if split is None or split[0] is None:
        return (None, None)
    split = split[0]
    return ((split[0]+sep(rest)+rest,),(split[1]+sep(rest)+rest,),), ((right,),(right,),)


right_or_r = Rule('right or_r',
        symbolic="... => ... v A // ... => A",
        docs="Rozkładanie alternatywy po prawej stronie sekwentu",
        reusable=None # Not needed
)

@make_right(rule=right_or_r)
def func_right_or_r(left: utils.Sentence, right: utils.Sentence):
    """ ... => (A,B)[side]
        ______________
        ... => AvB
    """
    if not right:
        return (None, None)
    
    split = utils.strip_around(right, 'or', False)
    if split is None or split[0] is None:
        return (None, None)
    left_split, right_split = split[0]
    
    return ((left,),), ((right_split,),)


right_or_l = Rule('right or_l',
        symbolic="... => A v ... // ... => A",
        docs="Rozkładanie alternatywy po prawej stronie sekwentu",
        reusable=None # Not needed
)

@make_right(rule=right_or_l)
def func_right_or_l(left: utils.Sentence, right: utils.Sentence):
    """ ... => (A,B)[side]
        ______________
        ... => AvB
    """
    if not right:
        return (None, None)
    
    split = utils.strip_around(right, 'or', False)
    if split is None or split[0] is None:
        return (None, None)
    left_split, right_split = split[0]
    
    return ((left,),), ((left_split,),)


left_imp = Rule('left imp',
        symbolic="..., A -> B => ... // ..., A => B | ..., B => ...",
        docs="Rozkładanie implikacji po lewej stronie sekwentu",
        reusable=None # Not needed            
)

@make_left(rule=left_imp)
def func_left_imp(left: utils.Sentence, right: utils.Sentence, num: int):
    """ A -> B, ... => A    B,... => ...
        ________________________________
        A -> B,... => ...
    """
    conj, rest = pop_part(left, num)
    if conj is None:
        return (None, None)
    
    split = utils.strip_around(conj, 'imp', False)
    if split is None or split[0] is None:
        return (None, None)
    split = split[0]
    return ((conj+sep(rest)+rest,),(split[1]+sep(rest)+rest,),), ((split[0],),(right,),)


right_imp = Rule('right imp',
        symbolic="A, A, ... => ... // A, ... => ...",
        docs="Reguła osłabiania lewej strony",
        reusable=None # Not needed
)

@make_right(rule=right_imp)
def func_right_imp(left: utils.Sentence, right: utils.Sentence):
    """ ..., A => B
        ______________
        ... => A -> B
    """
    split = utils.strip_around(right, 'imp', False)
    if split is None or split[0] is None:
        return (None, None)
    split = split[0]
    return ((split[0]+sep(left)+left,),), ((split[1],),)

left_and.children = [right_imp]
right_imp.children = [right_and]
right_and.children = [left_or]
left_or.children = [left_imp]
left_imp.children = [right_or_l]
right_or_l.children = [right_or_r]


_r = [
    right_and, right_imp, right_or_l, right_or_r,
    left_and, left_imp, left_or
]

RULES = {i.name:i for i in _r}