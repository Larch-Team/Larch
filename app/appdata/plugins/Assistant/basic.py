from article import Article
from exceptions import UserMistake
from proof import Proof
from typing import Union

SOCKET = 'Assistant'
VERSION = '0.0.1'


# Knowledge base

def get_articles(lang: str) -> dict[str, Article]:
    """
    Return all of the articles with their names as keys
    """
    return {}


def rule_docs(rule: str, lang: str) -> Union[str, None]:
    """
    Zwraca dokumentację reguły
    
    :param rule: Nazwa reguły
    :type rule: str
    :param lang: Nazwa języka (zgodnie z http://www.lingoes.net/en/translator/langcode.htm)
    :type lang: str
    :return: Opis reguły
    :rtype: list[str] | None
    """
    pass


def context_docs(context: str, rule: str, lang: str) -> Union[tuple[str, str], None]:
    """
    Zwraca nazwę oraz dokumentację kontekstu danej reguły
    
    :param context: Nazwa kontekstu
    :type context: str
    :param rule: Nazwa reguły
    :type rule: str
    :param lang: Nazwa języka (zgodnie z http://www.lingoes.net/en/translator/langcode.htm)
    :type lang: str
    :return: Opis elementu
    :rtype: tuple[str, str] | None
    """
    pass
    
# Hints

def hint_command(proof: Union[Proof, None], lang: str) -> Union[list[str], None]:
    """
    Wykonywana przy wywołaniu przez użytkownika pomocy.
    Proof to faktyczny dowód, zachowaj ostrożność.

    :param proof: Aktualny obiekt dowodu
    :type proof: Proof | None
    :return: Lista podpowiedzi, jeden str na odpowiedź
    :rtype: list[str] | None
    """
    pass


def hint_start(lang: str) -> Union[list[str], None]:
    """
    Wykonywana przy rozpoczęciu nowego dowodu

    :return: Lista podpowiedzi, jeden str na odpowiedź
    :rtype: list[str] | None
    """
    if lang.startswith('en'):
        return ["<b>Logic -> Psyche</b>", "Good luck!"]
    elif lang.startswith('pl'):
        return ["<b>Logika -> Psychika</b>", "Powodzenia!"]


# Mistake correction

def mistake_userule(mistake: UserMistake, lang: str) -> Union[list[str], None]:
    """
    Wykonywana przy wywołaniu przez użytkownika pomocy

    :param proof: Aktualny obiekt dowodu
    :type proof: Proof | None
    :return: Lista podpowiedzi, jeden str na odpowiedź
    :rtype: list[str] | None
    """
    pass


def mistake_check(mistake: UserMistake, lang: str) -> Union[list[str], None]:
    """
    Wywoływany do interpretacji błędu zwróconego przez socket Formal podczas sprawdzania dowodu

    :param mistake: Obiekt popełnionego błędu
    :type mistake: UserMistake
    :return: Lista podpowiedzi, jeden str na odpowiedź
    :rtype: list[str] | None
    """
    pass


def mistake_syntax(mistake: UserMistake, lang: str) -> Union[list[str], None]:
    """
    Wywoływany do interpretacji błędu zwróconego przez socket Formal podczas sprawdzania syntaksu

    :param mistake: Obiekt popełnionego błędu
    :type mistake: UserMistake
    :return: Lista podpowiedzi, jeden str na odpowiedź
    :rtype: list[str] | None
    """
    pass