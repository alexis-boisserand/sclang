import re
from enum import Enum
from itertools import takewhile
from schematics.types import StringType
from schematics.exceptions import ValidationError

_lower_case = re.compile(r'([a-z]+_?)*[a-z]')
_upper_case = re.compile(r'([A-Z]+_?)*[A-Z]')
_camel_case = re.compile(r'[A-Z][a-zA-Z]*')
_lower_camel_case = re.compile(r'[a-z][a-zA-Z]*')


class AutoNumber(Enum):
    def __new__(cls):
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj


class NamingStyle(AutoNumber):
    LOWER_CASE = ()
    UPPER_CASE = ()
    CAMEL_CASE = ()
    LOWER_CAMEL_CASE = ()
    OTHER = ()


def naming_style(str_):
    if _lower_case.fullmatch(str_):
        return NamingStyle.LOWER_CASE
    if _upper_case.fullmatch(str_):
        return NamingStyle.UPPER_CASE
    if _camel_case.fullmatch(str_):
        return NamingStyle.CAMEL_CASE
    if _lower_camel_case.fullmatch(str_):
        return NamingStyle.LOWER_CAMEL_CASE
    return NamingStyle.OTHER


def tokenize_camel_case(str_):
    tokens = []
    token = ''
    for c in str_:
        if c.isupper():
            if token != '':
                tokens.append(token)
            token = c
        else:
            token += c
    if token != '':
        tokens.append(token)
    return tokens


def to_camel_case(tokens):
    return ''.join([token[:1].upper() + token[1:].lower() for token in tokens])


def normalize(str_, style):
    input_style = naming_style(str_)
    if style in [input_style, NamingStyle.OTHER]:
        return str_

    if input_style in [NamingStyle.LOWER_CASE, NamingStyle.UPPER_CASE]:
        tokens = str_.split('_')
    elif input_style is NamingStyle.CAMEL_CASE:
        tokens = tokenize_camel_case(str_)
    elif input_style is NamingStyle.LOWER_CAMEL_CASE:
        first_token = ''
        for c in str_:
            if c.islower():
                first_token += c
            else:
                break
        other_tokens = tokenize_camel_case(str_[len(first_token):])
        tokens = [first_token] + other_tokens
    else:
        assert False, 'unknown input style'

    if style == NamingStyle.LOWER_CASE:
        return '_'.join([token.lower() for token in tokens])

    if style == NamingStyle.UPPER_CASE:
        return '_'.join([token.upper() for token in tokens])

    if style == NamingStyle.CAMEL_CASE:
        return to_camel_case(tokens)

    if style == NamingStyle.LOWER_CAMEL_CASE:
        return tokens[0].lower() + to_camel_case(tokens[1:])

    assert False, 'unknown style'


def lower_case(str_):
    return normalize(str_, NamingStyle.LOWER_CASE)


def upper_case(str_):
    return normalize(str_, NamingStyle.UPPER_CASE)


def camel_case(str_):
    return normalize(str_, NamingStyle.CAMEL_CASE)


def lower_camel_case(str_):
    return normalize(str_, NamingStyle.LOWER_CAMEL_CASE)


class NormalizedStringType(StringType):
    def validate(self, value, context=None):
        super().validate(value, context)
        if naming_style(value) is NamingStyle.OTHER:
            raise ValidationError(
                'naming style must be CamelCase, lowerCamelCase, UPPER_CASE or lower_case'
            )
        return value
