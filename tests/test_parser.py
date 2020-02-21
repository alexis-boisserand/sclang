from sclang import parse, ParsingError, DefinitionError
import pytest


def test_simplest():
    input = '''
off
  BUTTON_PRESS -> on
  TIMEOUT -> off

on
  TIMEOUT -> off
'''

    sc = parse(input)
    assert len(sc.states) == 2
    assert sc.states[0].name == 'off'
    assert sc.states[1].transitions[0].event == 'TIMEOUT'


def test_garbage_input():
    input = '%khcvbk'
    with pytest.raises(ParsingError):
        parse(input)


def test_wrong_indentation():
    input = '''
off
  BUTTON_PRESS -> on
    TIMEOUT -> off

on
  TIMEOUT -> off
'''
    with pytest.raises(ParsingError):
        parse(input)


def test_invalid_state_name():
    input = '''
off
  BUTTON_PRESS -> _on
  TIMEOUT -> off

_on
  TIMEOUT -> off
'''
    with pytest.raises(ParsingError):
        parse(input)


def test_invalid_event_name():
    input = '''
off
  BUTTON_PRESS -> on
  TIMEOUT -> off

on
  _TIMEOUT -> off
'''
    with pytest.raises(ParsingError):
        parse(input)


def test_not_unique_test_names():
    input = '''
off
  BUTTON_PRESS -> on
  TIMEOUT -> off

on
  TIMEOUT -> off

off
  TIMEOUT -> on
'''
    with pytest.raises(ParsingError):
        parse(input)


def test_invalid_target_name():
    input = '''
off
  BUTTON_PRESS -> on
  TIMEOUT -> off

on
  TIMEOUT -> offf
'''
    with pytest.raises(ParsingError):
        parse(input)


def test_unreachable_state():
    input = '''
off
  BUTTON_PRESS -> off
  TIMEOUT -> off

on
  TIMEOUT -> off
'''
    with pytest.raises(ParsingError):
        parse(input)


def test_invalid_transition():
    input = '''
off
  BUTTON_PRESS -> on
  TIMEOUT -> off
  BUTTON_PRESS -> off

on
  TIMEOUT -> off
'''
    with pytest.raises(ParsingError):
        parse(input)
