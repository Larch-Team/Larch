from article import Article
from exceptions import UserMistake
from proof import Proof
import typing as tp

SOCKET = 'Assistant'
VERSION = '0.2.0'


# Knowledge base

def get_articles(lang: str) -> dict[str, Article]:
    """
    Return all of the articles with their names as keys. 
    
    :param lang: Nazwa języka (zgodnie z http://www.lingoes.net/en/translator/langcode.htm)
    :type lang: str
    """
    pass

def rule_docs(rule: str, lang: str) -> tp.Union[str, None]:
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


def context_docs(context: str, rule: str, lang: str) -> tp.Union[tuple[str, str], None]:
    """
    Zwraca nazwę oraz dokumentację kontekstu danej reguły
    
    :param context: Nazwa kontekstu (variable)
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

def hint_command(proof: tp.Union[Proof, None], lang: str) -> tp.Union[list[str], None]:
    """
    Wykonywana przy wywołaniu przez użytkownika pomocy.
    Proof to faktyczny dowód, zachowaj ostrożność.

    :param proof: Aktualny obiekt dowodu
    :type proof: Proof | None
    :param lang: Nazwa języka (zgodnie z http://www.lingoes.net/en/translator/langcode.htm)
    :type lang: str
    :return: Lista podpowiedzi, jeden str na odpowiedź
    :rtype: list[str] | None
    """
    pass


def hint_start(lang: str) -> tp.Union[list[str], None]:
    """
    Wykonywana przy rozpoczęciu nowego dowodu

    :param lang: Nazwa języka (zgodnie z http://www.lingoes.net/en/translator/langcode.htm)
    :type lang: str
    :return: Lista podpowiedzi, jeden str na odpowiedź
    :rtype: list[str] | None
    """
    pass


# Mistake correction

def mistake_userule(mistake: UserMistake, lang: str) -> tp.Union[list[str], None]:
    """
    Wykonywana przy wywołaniu przez użytkownika pomocy

    :param proof: Aktualny obiekt dowodu
    :type proof: Proof | None
    :param lang: Nazwa języka (zgodnie z http://www.lingoes.net/en/translator/langcode.htm)
    :type lang: str
    :return: Lista podpowiedzi, jeden str na odpowiedź
    :rtype: list[str] | None
    """
    pass


def mistake_check(mistake: UserMistake, lang: str) -> tp.Union[list[str], None]:
    """
    Wywoływany do interpretacji błędu zwróconego przez socket Formal podczas sprawdzania dowodu

    :param mistake: Obiekt popełnionego błędu
    :type mistake: UserMistake
    :param lang: Nazwa języka (zgodnie z http://www.lingoes.net/en/translator/langcode.htm)
    :type lang: str
    :return: Lista podpowiedzi, jeden str na odpowiedź
    :rtype: list[str] | None
    """
    pass


def mistake_syntax(mistake: UserMistake, lang: str) -> tp.Union[list[str], None]:
    """
    Wywoływany do interpretacji błędu zwróconego przez socket Formal podczas sprawdzania syntaksu

    :param mistake: Obiekt popełnionego błędu
    :type mistake: UserMistake
    :param lang: Nazwa języka (zgodnie z http://www.lingoes.net/en/translator/langcode.htm)
    :type lang: str
    :return: Lista podpowiedzi, jeden str na odpowiedź
    :rtype: list[str] | None
    """
    pass