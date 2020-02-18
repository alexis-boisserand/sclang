import pytest
from scgen.normalize import NamingStyle, naming_style, normalize

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
    ('CamelCase', NamingStyle.CAMEL_CASE, 'CamelCase'),
    ('CamelCase', NamingStyle.LOWER_CAMEL_CASE, 'camelCase'),
    ('CamelCase', NamingStyle.UPPER_CASE, 'CAMEL_CASE'),
    ('CamelCase', NamingStyle.LOWER_CASE, 'camel_case'),
    ('CamelCase', NamingStyle.OTHER, 'CamelCase'),
    ('lowerCamelCase', NamingStyle.CAMEL_CASE, 'LowerCamelCase'),
    ('lowerCamelCase', NamingStyle.LOWER_CAMEL_CASE, 'lowerCamelCase'),
    ('lowerCamelCase', NamingStyle.UPPER_CASE, 'LOWER_CAMEL_CASE'),
    ('lowerCamelCase', NamingStyle.LOWER_CASE, 'lower_camel_case'),
    ('lowerCamelCase', NamingStyle.OTHER, 'lowerCamelCase'),
    ('UPPER_CASE', NamingStyle.CAMEL_CASE, 'UpperCase'),
    ('UPPER_CASE', NamingStyle.LOWER_CAMEL_CASE, 'upperCase'),
    ('UPPER_CASE', NamingStyle.UPPER_CASE, 'UPPER_CASE'),
    ('UPPER_CASE', NamingStyle.LOWER_CASE, 'upper_case'),
    ('UPPER_CASE', NamingStyle.OTHER, 'UPPER_CASE'),
    ('lower_case', NamingStyle.CAMEL_CASE, 'LowerCase'),
    ('lower_case', NamingStyle.LOWER_CAMEL_CASE, 'lowerCase'),
    ('lower_case', NamingStyle.UPPER_CASE, 'LOWER_CASE'),
    ('lower_case', NamingStyle.LOWER_CASE, 'lower_case'),
    ('lower_case', NamingStyle.OTHER, 'lower_case'),
]


@pytest.mark.parametrize('input, style, output', normalize_cases)
def test_normalize(input, style, output):
    assert normalize(input, style) == output
