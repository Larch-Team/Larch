"""
Tutaj umieść dokumentację swojego pluginu
"""
import typing as tp

SOCKET = 'Translate'
VERSION = '0.0.1'

def lang_code() -> str:
    return 'en'

def translate_engine(phrase: str) -> str:
    return phrase

def translate_UI(plugin: str, phrase: str) -> str:
    return phrase