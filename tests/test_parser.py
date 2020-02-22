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
    assert sc.states[1].event_handlers[0].event == 'TIMEOUT'


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


def test_state_names_not_unique():
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


def test_transition_not_unique():
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


def test_guard():
    input = '''
off
  BUTTON_PRESS -> on
  TIMEOUT["count == 3"] -> off

on
  TIMEOUT -> off
'''
    sc = parse(input)
    assert sc.states[0].event_handlers[1].transitions[0].guard == 'count == 3'


def test_multiple_guards():
    input = '''
off
  BUTTON_PRESS -> on
  TIMEOUT ["count == 3"] -> off
          ["count == 4"] -> on
          [else] -> on

on
  TIMEOUT -> off
'''
    sc = parse(input)
    assert sc.states[0].event_handlers[1].transitions[0].guard == 'count == 3'
    assert sc.states[0].event_handlers[1].transitions[1].guard == 'count == 4'
    assert not sc.states[0].event_handlers[1].transitions[1].has_else_guard()
    assert sc.states[0].event_handlers[1].transitions[2].has_else_guard()
