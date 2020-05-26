import pytest
from sclang.lib.normalize import NamingStyle, naming_style, normalize

naming_style_cases = [('Camel', NamingStyle.CAMEL_CASE),
                      ('CamelCase', NamingStyle.CAMEL_CASE),
                      ('lowerCamelCase', NamingStyle.LOWER_CAMEL_CASE),
                      ('UPPER', NamingStyle.UPPER_CASE),
                      ('UPPER_CASE', NamingStyle.UPPER_CASE),
                      ('UPPER_CASE_', NamingStyle.OTHER),
                      ('_UPPER_CASE', NamingStyle.OTHER),
                      ('__UPPER_CASE', NamingStyle.OTHER),
                      ('_UPPER__CASE', NamingStyle.OTHER),
                      ('UPPER_CASE__', NamingStyle.OTHER),
                      ('', NamingStyle.OTHER),
                      ('lower', NamingStyle.LOWER_CASE),
                      ('lower_case', NamingStyle.LOWER_CASE),
                      ('_lower_case', NamingStyle.OTHER),
                      ('lower__case', NamingStyle.OTHER),
                      ('__lower_case', NamingStyle.OTHER),
                      ('lower_case__', NamingStyle.OTHER),
                      ('NotCamel_Case', NamingStyle.OTHER),
                      ('Not_CamelCASEEither', NamingStyle.OTHER),
                      ('Not_CamelCASEEither', NamingStyle.OTHER)]


@pytest.mark.parametrize('input, output', naming_style_cases)
def test_naming_style(input, output):
    assert naming_style(input) is output


normalize_cases = [
    (NamingStyle.CAMEL_CASE, ('CamelCase', ), 'CamelCase'),
    (NamingStyle.LOWER_CAMEL_CASE, ('CamelCase', ), 'camelCase'),
    (NamingStyle.UPPER_CASE, ('CamelCase', ), 'CAMEL_CASE'),
    (NamingStyle.LOWER_CASE, ('CamelCase', ), 'camel_case'),
    (NamingStyle.CAMEL_CASE, ('lowerCamelCase', ), 'LowerCamelCase'),
    (NamingStyle.LOWER_CAMEL_CASE, ('lowerCamelCase', ), 'lowerCamelCase'),
    (NamingStyle.UPPER_CASE, ('lowerCamelCase', ), 'LOWER_CAMEL_CASE'),
    (NamingStyle.LOWER_CASE, ('lowerCamelCase', ), 'lower_camel_case'),
    (NamingStyle.CAMEL_CASE, ('UPPER_CASE', ), 'UpperCase'),
    (NamingStyle.LOWER_CAMEL_CASE, ('UPPER_CASE', ), 'upperCase'),
    (NamingStyle.UPPER_CASE, ('UPPER_CASE', ), 'UPPER_CASE'),
    (NamingStyle.LOWER_CASE, ('UPPER_CASE', ), 'upper_case'),
    (NamingStyle.CAMEL_CASE, ('lower_case', ), 'LowerCase'),
    (NamingStyle.LOWER_CAMEL_CASE, ('lower_case', ), 'lowerCase'),
    (NamingStyle.UPPER_CASE, ('lower_case', ), 'LOWER_CASE'),
    (NamingStyle.LOWER_CASE, ('lower_case', ), 'lower_case'),
    (NamingStyle.OTHER, ('lower_case', ), None),
    (NamingStyle.LOWER_CASE, ('strange_Style', ), None),
    (NamingStyle.CAMEL_CASE, (
        'CamelCase',
        'lower_case',
        'UPPER_CASE',
        'lowerCamelCase',
    ), 'CamelCaseLowerCaseUpperCaseLowerCamelCase'),
    (NamingStyle.LOWER_CAMEL_CASE, (
        'lower_case',
        'CamelCase',
        'UPPER_CASE',
        'lowerCamelCase',
    ), 'lowerCaseCamelCaseUpperCaseLowerCamelCase'),
    (NamingStyle.UPPER_CASE, (
        'lower_case',
        'CamelCase',
        'UPPER_CASE',
        'lowerCamelCase',
    ), 'LOWER_CASE_CAMEL_CASE_UPPER_CASE_LOWER_CAMEL_CASE'),
    (NamingStyle.LOWER_CASE, (
        'lower_case',
        'CamelCase',
        'UPPER_CASE',
        'lowerCamelCase',
    ), 'lower_case_camel_case_upper_case_lower_camel_case'),
]


@pytest.mark.parametrize('style, input, output', normalize_cases)
def test_normalize(style, input, output):
    if output is None:
        with pytest.raises(AssertionError):
            normalize(style, *input)
    else:
        assert normalize(style, *input) == output
