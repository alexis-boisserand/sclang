from sclang import parse, ParsingError
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
    pass


def test_invalid_state_name():
    pass


def test_invalid_event_name():
    pass


def test_not_unique_test_names():
    pass


def test_invalid_target_name():
    pass


def test_unreachable_state():
    pass


def test_invalid_transition():
    pass
