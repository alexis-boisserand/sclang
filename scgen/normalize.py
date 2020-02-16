import re
from enum import Enum
from schematics.types import StringType
from schematics.exceptions import ValidationError

_lower_case = re.compile(r'([a-z]+_?)*[a-z]')
_upper_case = re.compile(r'([A-Z]+_?)*[A-Z]')
_camel_case = re.compile(r'([A-Z][a-z]*)+')


class AutoNumber(Enum):
    def __new__(cls):
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj


class NamingStyle(AutoNumber):
    CAMEL_CASE = ()
    UPPER_CASE = ()
    LOWER_CASE = ()
    OTHER = ()


def naming_style(str_):
    if _lower_case.fullmatch(str_):
        return NamingStyle.LOWER_CASE
    if _upper_case.fullmatch(str_):
        return NamingStyle.UPPER_CASE
    if _camel_case.fullmatch(str_):
        return NamingStyle.CAMEL_CASE
    return NamingStyle.OTHER


def normalize(str_, style):
    input_style = naming_style(str_)
    if style in [input_style, NamingStyle.OTHER]:
        return str_

    if input_style in [NamingStyle.LOWER_CASE, NamingStyle.UPPER_CASE]:
        tokens = str_.split('_')
    elif input_style is NamingStyle.CAMEL_CASE:
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
    else:
        assert False, 'unknown input style'

    if style == NamingStyle.LOWER_CASE:
        return '_'.join([token.lower() for token in tokens])

    if style == NamingStyle.UPPER_CASE:
        return '_'.join([token.upper() for token in tokens])

    if style == NamingStyle.CAMEL_CASE:
        return ''.join(
            [token[:1].upper() + token[1:].lower() for token in tokens])

    assert False, 'unknown style'


def lower_case(str_):
    return normalize(str_, NamingStyle.LOWER_CASE)


def upper_case(str_):
    return normalize(str_, NamingStyle.UPPER_CASE)


def camel_case(str_):
    return normalize(str_, NamingStyle.CAMEL_CASE)


class NormalizedStringType(StringType):
    def validate(self, value, context=None):
        super().validate(value, context)
        if naming_style(value) is NamingStyle.OTHER:
            raise ValidationError(
                'naming style must be CamelCase, UPPER_CASE or lower_case')
        return value
