from sclang import parse
import pytest

event_names_params = [('''
/some_name
off
  @BUTTON_PRESS -> on
  @TIMEOUT -> off

on
  @TIMEOUT -> off
''', ['BUTTON_PRESS', 'TIMEOUT']),
                      ('''
/some_name
@YO -> some_name
off
  @BUTTON_PRESS -> on
  @TIMEOUT -> off
  not_really_off
    @SOME_EVENT -> really_off
  really_off
    @OTHER_EVENT -> not_really_off
on
  @TIMEOUT -> off
''', ['YO', 'BUTTON_PRESS', 'TIMEOUT', 'SOME_EVENT', 'OTHER_EVENT'])]


@pytest.mark.parametrize('input, events', event_names_params)
def test_event_names(input, events):
    sc = parse(input)
    assert sc.event_names == set(events)


def test_all_states():
    input = '''
/some_name
off
  @BUTTON_PRESS -> on
  @TIMEOUT -> off
  not_really_off
    @SOME_EVENT -> really_off
    what
  really_off
    @OTHER_EVENT -> not_really_off
on
  @TIMEOUT -> off
'''
    sc = parse(input)
    assert sc.all_states == [
        sc, sc.states[0], sc.states[0].states[0],
        sc.states[0].states[0].states[0], sc.states[0].states[1], sc.states[1]
    ]


def test_path():
    input = '''
/some_name
off
  @BUTTON_PRESS -> on
  @TIMEOUT -> off
  not_really_off
    @SOME_EVENT -> really_off
    what
  really_off
    @OTHER_EVENT -> not_really_off
on
  @TIMEOUT -> off
'''
    sc = parse(input)
    assert sc.states[0].path == 'some_name/off'
    assert sc.states[0].states[1].path == 'some_name/off/really_off'
    assert sc.states[0].states[0].states[
        0].path == 'some_name/off/not_really_off/what'
