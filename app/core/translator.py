
from typing import Any, Callable, Iterable
from exceptions import EngineError
import inspect

def spare_transl(func: Callable) -> Callable:
    func.spare = True
    return func

def translate_exceptions(func: Callable[..., Any]) -> Callable[..., Any]:
    def wrapper(sess, *args, **kwargs):
        if not (translator := sess.acc('Translate').translate_engine):
            translator = lambda x: x
        try:
            return func(sess, *args, **kwargs)
        except EngineError as e:
            raise EngineError(translator(str(e)))
    return wrapper

def translate_string(func: Callable[..., str]) -> Callable[..., str]:
    def wrapper(sess, *args, **kwargs):
        if not (translator := sess.acc('Translate').translate_engine):
            translator = lambda x: x
        try:
            return translator(func(sess, *args, **kwargs))
        except EngineError as e:
            raise EngineError(translator(str(e)))
    return wrapper

def translate_tuple(func: Callable[..., tuple[str]]) -> Callable[..., tuple[str]]:
    def wrapper(sess, *args, **kwargs):
        # sourcery skip: comprehension-to-generator
        if not (translator := sess.acc('Translate').translate_engine):
            translator = lambda x: x
        try:
            return tuple([translator(i) for i in func(sess, *args, **kwargs)])
        except EngineError as e:
            raise EngineError(translator(str(e)))
    return wrapper

def translate_generator(func: Callable[..., Iterable[str]]) -> Callable[..., Iterable[str]]:
    def wrapper(sess, *args, **kwargs):
        if not (translator := sess.acc('Translate').translate_engine):
            translator = lambda x: x
        try:
            return translator(func(sess, *args, **kwargs))
        except EngineError as e:
            raise EngineError(translator(str(e)))
    return wrapper

def translate(func: Callable[..., Any]) -> Callable[..., Any]:
    if not func.__annotations__.get("return"):
        return translate_exceptions(func)
    else:
        sig = inspect.signature(func).return_annotation
    
    if sig == 'str':
        dec = translate_string
    elif sig == 'Iterable[str]':
        dec = translate_generator
    elif sig == 'tuple[str]':
        dec = translate_tuple
    else:
        dec = translate_exceptions
    return dec(func)

def translate_all(cls):
        for name, method in inspect.getmembers(cls, inspect.isfunction):
            if not hasattr(method, 'spare'):
                setattr(cls, name, translate(method))

        return cls
