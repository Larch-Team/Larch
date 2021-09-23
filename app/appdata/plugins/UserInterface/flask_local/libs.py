
from typing import Any, Iterator
from string import Template

from sentence import Sentence

def JSONResponse(type_: str, content: Any = None):
    return {'type':type_, 'content': content} if content is not None else {'type':type_}

def symbol_HTML(rule: str):
    rule = rule.replace(";", "<br>").replace("|", "</div> <div>")
    premiss, result = rule.split(" / ")
    return f'<div class="symbolic"><div>{premiss}</div></div> <hr> <div class="symbolic"><div>{result}</div></div>'
    

# TODO: uzupełnić tag
Tag = Template('<button type="button" class="rule_button" onclick="use_rule(\'$branch\', $tID, $sID)">$symbol</button>')

def _clickable(sentence: Sentence, sentenceID: int, branch: str) -> Iterator[str]:
    for tID, symbol in enumerate(sentence.getReadableList()):
        yield Tag.substitute(tID=tID, sID=sentenceID, branch=branch, symbol=symbol)

def get_clickable(sentence: Sentence, sentenceID: int, branch: str):
    return " ".join(_clickable(sentence, sentenceID, branch))