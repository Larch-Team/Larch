from typing import Iterable, Optional
from sentence import Sentence


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
    return buffor == s

def list_parts(sentence: Sentence) -> Iterable[Sentence]:
    p = []
    for i in sentence:
        if i.startswith('sep'):
            yield Sentence(p, sentence.S)
            p = []
        else:
            p.append(i)
    yield Sentence(p, sentence.S)

def find_rules(sentence: Sentence) -> list[tuple[str, Optional[int]]]:
    _, (left, right) = sentence.getComponents()

    p, _ = right.getComponents()
    if p is not None:
        if p.startswith('or'):
            possible = [("right or_l", None), ("right or_r", None)]
        else:
            possible = [("right "+p.split('_')[0], None)]
    ln = 1
    for i in list_parts(left):
        p, _ = i.getComponents()
        if p is not None:
            possible.append(("left "+p.split('_')[0], ln))
        ln += len(i)+1
    return possible

def sep(part: Sentence = None) -> list[str]:
        if part is None or (len(part)>0 and not part[0].startswith('sep')):
            return ['sep_;']
        else:
            return []
        
def pop_part(sentence: Sentence, n: int):
    """
    Zwraca podzdanie zawierający n-ty token, oprócz tego zwraca wersję z usuniętym zdaniem
    """
    s = []
    chosen = None
    for i in list_parts(sentence):
        if len(s+i)>n:
            chosen = i
        elif s == []:
            s = i
        else:
            s.append('sep_;')
            s.extend(i)
            

    if chosen is None:
        return None, None
    return chosen, s