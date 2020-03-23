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


def test_path_elements():
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
    assert sc.states[0].path_elements == ['some_name', 'off']
    assert sc.states[0].states[1].path_elements == [
        'some_name', 'off', 'really_off'
    ]
    assert sc.states[0].states[0].states[0].path_elements == [
        'some_name', 'off', 'not_really_off', 'what'
    ]


def test_state_paths():
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
    assert list(sc.state_paths.values()) == list(sc.all_states)
    assert list(sc.state_paths.keys()) == [
        'some_name', 'some_name/off', 'some_name/off/not_really_off',
        'some_name/off/not_really_off/what', 'some_name/off/really_off',
        'some_name/on'
    ]
    assert sc.state_paths is sc.states[0].state_paths


def test_common_ancestor():
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
    assert sc.common_ancestor(sc) is sc
    assert sc.states[0].states[0].common_ancestor(
        sc.states[0].states[0]) is sc.states[0].states[0]
    assert sc.states[0].states[0].common_ancestor(
        sc.states[0].states[1]) is sc.states[0]
    assert sc.states[0].states[1].common_ancestor(
        sc.states[0].states[0].states[0]) is sc.states[0]


def test_states_to_ancestor():
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
    what
      @EVENT->final
    final
on
  @TIMEOUT -> off
'''
    sc = parse(input)
    assert sc.states[0].states[0].states_to_ancestor(sc) == [sc.states[0]]
    assert sc.states[0].states[0].states[0].states_to_ancestor(sc) == [
        sc.states[0].states[0], sc.states[0]
    ]
    assert sc.states[0].states[1].states[1].states_to_ancestor(sc) == [
        sc.states[0].states[1], sc.states[0]
    ]
    assert sc.states[0].states[1].states[0].states_to_ancestor(sc) == [
        sc.states[0].states[1], sc.states[0]
    ]
    assert sc.states[0].states[0].states_to_ancestor(sc.states[0]) == []
    assert sc.states[0].states[0].states_to_ancestor(
        sc.states[0].states[0]) == []
