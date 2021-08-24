from typing import  Optional
from rule import Rule
from proof import Proof
import plugins.Formal.__utils__ as utils
from sentence import Sentence
from tree import ProofNode
from rules import left_imp, RULES
from libs import find_rules, is_sequent, check_closure

from usedrule import UsedRule
    

def use_strict(proof: Proof, rule: Rule, branch_name: str, part: Optional[int]) -> list[str]:
    leaf = proof.nodes.getleaf(branch_name)
    branch, _ = leaf.getbranch_sentences()
    _, (start_left, start_right) = leaf.sentence.getComponents()
    start_left, start_right = start_left or Sentence([], None), start_right or Sentence([], None)

    history = None
    if rule.name == "left imp":
        assert start_right not in leaf.history
        history = [[start_right], [0]]
    elif rule.name == 'left or':
        history = [[-1], [-1]]
    elif rule.name == 'right imp':
        l = utils.strip_around(start_right, "imp", False)
        history = [[0]] if is_sequent(start_left, l[0][0]) else [[-1]]
    
    fin = rule.strict(leaf.sentence, part) if part else rule.strict(leaf.sentence)
    assert fin is not None, "Reguła nie zwróciła nic"
    layer = proof.append(fin, branch_name)

    # History length multiplication
    if not history:
        history = [[0]]*len(fin)
    ProofNode.insert_history(history, leaf.children)

    context = {'tokenID': part} if part else {}
    
    proof.metadata['usedrules'].append(
        UsedRule(layer, branch_name, rule.name, proof, context, decisions={'sentenceID':len(branch)-1}))
    return [i.branch for i in leaf.children]

    
def possible_rules(proof: Proof) -> list[tuple[Rule, int, str]]:
    rules = []
    for i in proof.nodes.getleaves():
        r = find_rules(i.sentence)
        rules.extend([(RULES[rule], part, i.branch) for rule, part in r])
    return sorted(rules, key=sort_key)
    

def sort_key(x: tuple[Rule, int, str]) -> int:
    rule, part, branch = x
    return len(rule.ancestors)
     
    
def solve(proof: Proof) -> bool:
    for rule, part, branch in possible_rules(proof):
        if rule is left_imp:
            leaf = proof.nodes.getleaf(branch)
            _, (start_left, start_right) = leaf.sentence.getComponents()
            if start_right in leaf.history:
                continue

        brs = use_strict(proof, rule, branch, part)
        for i in brs:
            proof.deal_closure_func(check_closure, i)
        if not proof.nodes.is_closed():
            return solve(proof)
        if proof.nodes.is_successful():
            return True
        proof.nodes.pop(proof.metadata['usedrules'].pop().layer)
    return False
            