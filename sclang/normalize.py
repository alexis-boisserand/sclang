import re
from enum import Enum

lower_case_reg = re.compile(r'([a-z]+_?)*[a-z]')
upper_case_reg = re.compile(r'([A-Z]+_?)*[A-Z]')
camel_case_reg = re.compile(r'([A-Z][a-z]+)+')
lower_camel_case_reg = re.compile(r'([a-z]+[A-Z][a-z]+)+')


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


def naming_style(string):
    if lower_case_reg.fullmatch(string):
        return NamingStyle.LOWER_CASE
    if upper_case_reg.fullmatch(string):
        return NamingStyle.UPPER_CASE
    if camel_case_reg.fullmatch(string):
        return NamingStyle.CAMEL_CASE
    if lower_camel_case_reg.fullmatch(string):
        return NamingStyle.LOWER_CAMEL_CASE
    return NamingStyle.OTHER


def tokenize_camel_case(string):
    tokens = []
    token = ''
    for c in string:
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


def tokenize(input_style, string):
    if input_style in [NamingStyle.LOWER_CASE, NamingStyle.UPPER_CASE]:
        tokens = string.split('_')
    elif input_style is NamingStyle.CAMEL_CASE:
        tokens = tokenize_camel_case(string)
    elif input_style is NamingStyle.LOWER_CAMEL_CASE:
        first_token = ''
        for c in string:
            if c.islower():
                first_token += c
            else:
                break
        other_tokens = tokenize_camel_case(string[len(first_token):])
        tokens = [first_token] + other_tokens
    else:
        assert False, 'invalid input style'

    return tokens


def assemble(output_style, tokens):
    if output_style == NamingStyle.LOWER_CASE:
        return '_'.join([token.lower() for token in tokens])

    if output_style == NamingStyle.UPPER_CASE:
        return '_'.join([token.upper() for token in tokens])

    if output_style == NamingStyle.CAMEL_CASE:
        return to_camel_case(tokens)

    if output_style == NamingStyle.LOWER_CAMEL_CASE:
        return tokens[0].lower() + to_camel_case(tokens[1:])

    assert False, 'invalid output style'


def normalize(output_style, *string):
    assert not output_style is NamingStyle.OTHER
    tokens = []
    for s in string:
        input_style = naming_style(s)
        assert not input_style is NamingStyle.OTHER
        tokens.extend(tokenize(input_style, s))

    return assemble(output_style, tokens)


def lower_case(*string):
    return normalize(NamingStyle.LOWER_CASE, *string)


def upper_case(*string):
    return normalize(NamingStyle.UPPER_CASE, *string)


def camel_case(*string):
    return normalize(NamingStyle.CAMEL_CASE, *string)


def lower_camel_case(*string):
    return normalize(NamingStyle.LOWER_CAMEL_CASE, *string)
