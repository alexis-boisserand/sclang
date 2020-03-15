from sclang import parse, ParsingError, DefinitionError
import pytest


def test_simplest():
    input = '''
/simplest
off
  @BUTTON_PRESS -> on
  @TIMEOUT -> off

on
  @TIMEOUT -> off
'''

    sc = parse(input)
    assert sc.name == 'simplest'
    assert len(sc.states) == 2
    assert sc.states[0].name == 'off'
    assert sc.states[1].event_handlers[0].event == 'TIMEOUT'


def test_garbage_input():
    input = '%khcvbk'
    with pytest.raises(ParsingError):
        parse(input)


def test_wrong_indentation():
    input = '''
/some_name
off
  @BUTTON_PRESS -> on
    @TIMEOUT -> off

on
  @TIMEOUT -> off
'''
    with pytest.raises(ParsingError):
        parse(input)


def test_invalid_state_name():
    input = '''
/some_name
off
  @BUTTON_PRESS -> _on
  @TIMEOUT -> off

_on
  @TIMEOUT -> off
'''
    with pytest.raises(ParsingError):
        parse(input)


def test_invalid_event_name():
    input = '''
/some_name
off
  @BUTTON_PRESS -> on
  @TIMEOUT -> off

on
  @_TIMEOUT -> off
'''
    with pytest.raises(ParsingError):
        parse(input)


def test_state_names_not_unique():
    input = '''
/some_name
off
  @BUTTON_PRESS -> on
  @TIMEOUT -> off

on
  @TIMEOUT -> off

off
  @TIMEOUT -> on
'''
    with pytest.raises(DefinitionError) as exc:
        parse(input)
    assert 'state name not unique in state "some_name"' in str(exc.value)


def test_invalid_target_name():
    input = '''
/some_name
off
  @BUTTON_PRESS -> on
  @TIMEOUT -> off

on
  @TIMEOUT -> offf
'''
    with pytest.raises(DefinitionError) as exc:
        parse(input)
    assert 'invalid transition target "offf" in state "on"' in str(exc.value)


def test_unreachable_state():
    input = '''
/some_name
off
  @BUTTON_PRESS -> off
  @TIMEOUT -> off

on
  @TIMEOUT -> off
'''
    with pytest.raises(DefinitionError) as exc:
        parse(input)
    assert 'state "on" is unreachable' in str(exc.value)


def test_event_handlers_not_unique():
    input = '''
/some_name
off
  @BUTTON_PRESS -> on
  @TIMEOUT -> off
  @BUTTON_PRESS -> off

on
  @TIMEOUT -> off
'''
    with pytest.raises(DefinitionError) as exc:
        parse(input)
    assert 'event handler not unique in state "off"' in str(exc.value)


def test_guard():
    input = '''
/some_name
off
  @BUTTON_PRESS -> on
  @TIMEOUT
    ["count == 3"] -> off

on
  @TIMEOUT -> off
'''
    sc = parse(input)
    assert sc.states[0].event_handlers[1].transitions[0].guard == 'count == 3'


def test_multiple_guards():
    input = '''
/some_name
off
  @BUTTON_PRESS -> on
  @TIMEOUT
    ["count == 3"] -> off
    ["count == 4"] -> on
    [else] -> on

on
  @TIMEOUT -> off
'''
    sc = parse(input)
    assert sc.states[0].event_handlers[1].transitions[0].guard == 'count == 3'
    assert sc.states[0].event_handlers[1].transitions[1].guard == 'count == 4'
    assert not sc.states[0].event_handlers[1].transitions[1].is_else_guard
    assert sc.states[0].event_handlers[1].transitions[2].is_else_guard


def test_only_else_guard():
    input = '''
/some_name
off
  @BUTTON_PRESS -> on
  @TIMEOUT
    [else] -> on

on
  @TIMEOUT -> off
'''
    with pytest.raises(ParsingError):
        parse(input)


def test_else_not_final():
    input = '''
/some_name
off
  @BUTTON_PRESS -> on
  @TIMEOUT
    ["count == 3"] -> off
    [else] -> on
    ["count == 4"] -> on

on
  @TIMEOUT -> off
'''
    with pytest.raises(ParsingError):
        parse(input)


def test_else_guard_not_unique():
    input = '''
/some_name
off
  @BUTTON_PRESS -> on
  @TIMEOUT
    ["count == 3"] -> off
    [else] -> on
    [else] -> off

on
  @TIMEOUT -> off
'''
    with pytest.raises(ParsingError):
        parse(input)


def test_guard_not_unique():
    input = '''
/some_name
off
  @BUTTON_PRESS -> on
  @TIMEOUT
    ["count == 3"] -> off
    ["count == 3"] -> on
    [else] -> off

on
  @TIMEOUT -> off
'''
    with pytest.raises(DefinitionError) as exc:
        parse(input)
    assert 'guard not unique for event "TIMEOUT"' in str(exc.value)


def test_transient_state():
    input = '''
/some_name
<>off
  ["true"] -> on
  [else] -> off

on
  @TIMEOUT -> off
'''
    sc = parse(input)
    assert sc.initial.is_transient
    assert not sc.is_transient
    assert not sc.states[1].is_transient


def test_transient_state_with_guard_not_unique():
    input = '''
/some_name
<>off
  ["count == 3"] -> on
  ["count == 4"] -> on
  ["count == 4"] -> on
  [else] -> on

on
  @TIMEOUT -> off
'''
    with pytest.raises(DefinitionError) as exc:
        parse(input)

    assert 'guard not unique for event "None"' in str(exc.value)


def test_actions():
    input = '''
/some_name
#init
  "bonjour()"
#exit
  "auRevoir()"
off
  #init
    "doSomething()"
  @TIMEOUT
    ["count == 3"] -> on
  <>half_off
    ["count == 6"] -> other
      "set(6)"
    [else] -> yes
      "set(7)"
  yes
    #init
      "start()"
      "stop()"
    #exit
      "stop()"
      "start()"
  other

on
  #exit
    "doSomethingElse()"
  @TIMEOUT -> off
'''
    sc = parse(input)
    assert sc.init_actions == ['bonjour()']
    assert sc.exit_actions == ['auRevoir()']
    assert sc.states[0].init_actions == ['doSomething()']
    assert sc.states[0].states[0].transitions[0].actions == ['set(6)']
    assert sc.states[0].states[0].transitions[1].actions == ['set(7)']
    assert sc.states[1].exit_actions == ['doSomethingElse()']
    assert sc.states[0].states[1].init_actions == ['start()', 'stop()']
    assert sc.states[0].states[1].exit_actions == ['stop()', 'start()']


def test_internal_external_transition():
    input = '''
/some_name
off
  #init
    "doSomething()"
  @TIMEOUT
    ["count == 3"] -> on
  @OTHER
    ["count == 6"] --
      "set(6)"
    ["count == 4"] -> off
    [else] --
      "set(7)"
  yes
    #init
      "start()"
      "stop()"
    #exit
      "stop()"
      "start()"
    @TO_OTHER -> other
    @WHAT --
      "restart()"
  other

on
  #exit
    "doSomethingElse()"
  @SOME --
    "wait()"
  @TIMEOUT -> off
'''
    sc = parse(input)
    assert sc.states[0].transitions[1].is_internal
    assert sc.states[0].transitions[1].actions == ['set(6)']
    assert not sc.states[0].transitions[2].is_internal
    assert sc.states[0].transitions[3].is_internal
    assert sc.states[0].states[0].transitions[1].is_internal
    assert sc.states[0].states[0].transitions[1].actions == ['restart()']
    assert sc.states[1].transitions[0].is_internal


def test_internal_transition_without_action():
    input = '''
/some_name
off
  #init
    "doSomething()"
  @TIMEOUT
    ["count == 3"] -> on
  @OTHER
    ["count == 6"] --
      "set(6)"
    ["count == 4"] -> off
    [else] --
      "set(7)"
  yes
    #init
      "start()"
      "stop()"
    #exit
      "stop()"
      "start()"
    @TO_OTHER -> other
    @OTHER --
      "restart()"
  other

on
  #exit
    "doSomethingElse()"
  @SOME --
  @TIMEOUT -> off
'''
    with pytest.raises(ParsingError):
        parse(input)


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


def test_composite():
    input = '''
/some_name
off
  @BUTTON_PRESS -> on
  @TIMEOUT -> off
  not_really_off
    @SOME_EVENT -> really_off
  really_off
    @OTHER_EVENT -> not_really_off
on
  @TIMEOUT -> off
'''
    sc = parse(input)
    assert sc.is_root
    assert sc.states[0].states[0].name == 'not_really_off'
    assert sc.states[0].states[1].name == 'really_off'
    assert not sc.states[0].is_root
    assert not sc.states[0].states[1].is_root
    assert sc.states[0].is_initial
    assert not sc.states[1].is_initial
    assert sc.states[1].is_atomic
    assert not sc.states[0].is_atomic
    assert sc.states[0].states[0].is_initial
    assert sc.states[0].states[0].is_atomic


def test_composite_valid_target_path():
    input = '''
/some_name
off
  @BUTTON_PRESS -> on
  @TIMEOUT -> off
  not_really_off
    @SOME_EVENT -> ../off
    @EVENT -> really_off
    @THIRD_EVENT -> not_really_off/what
    what
  really_off
    @OTHER_EVENT -> ../on/what
on
  @TIMEOUT
    ["i==3"] -> off/really_off
    [else] -> off/not_really_off/what
  what
    @OTHER -> ../on
'''
    sc = parse(input)
    assert sc.states[0].states[0].transitions[
        2].target.path == 'some_name/off/not_really_off/what'


composite_invalid_transition_target_params = [('''
/some_name
off
  @BUTTON_PRESS -> on
  @TIMEOUT -> off
  not_really_off
    @SOME_EVENT -> ../off
    @EVENT -> really_off
    what
  really_off
    @OTHER_EVENT -> ../on
on
  @TIMEOUT
    ["i==3"] -> really_off
    [else] -> off/not_really_off/what
  what
    @OTHER -> ../off
''', 'really_off', 'on'),
                                              ('''
/some_name
off
  @BUTTON_PRESS -> on
  @TIMEOUT -> off
  not_really_off
    @SOME_EVENT -> ../off
    @EVENT -> really_off
    what
  really_off
    @OTHER_EVENT -> ../on
on
  @TIMEOUT
    ["i==3"] -> off/really_off
    [else] -> off/what
  what
    @OTHER -> ../off
''', 'off/what', 'on')]


@pytest.mark.parametrize('input, target, state',
                         composite_invalid_transition_target_params)
def test_composite_invalid_transition_target(input, target, state):
    with pytest.raises(DefinitionError) as exc:
        parse(input)
    assert 'invalid transition target "{}" in state "{}"'.format(
        target, state) in str(exc.value)


invalid_target_path_params = [('''
/some_name
@TIMEOUT -> ../off
off
  @BUTTON_PRESS -> on
  @TIMEOUT -> off
  @OTHER -> ../on
  not_really_off
    @SOME_EVENT -> ../off
    @EVENT -> really_off
    @THIRD_EVENT -> not_really_off/what
    what
  really_off
    @OTHER_EVENT -> ../on/what
on
  @TIMEOUT
    ["i==3"] -> off/really_off
    [else] -> off/not_really_off/what
  what
    @OTHER -> ../on
''', '../off', 'some_name'),
                              ('''
/some_name
off
  @BUTTON_PRESS -> on
  @TIMEOUT -> off
  not_really_off
    @SOME_EVENT -> ../../../off
    @EVENT -> really_off
    @THIRD_EVENT -> not_really_off/what
    what
  really_off
    @OTHER_EVENT -> ../on/what
on
  @TIMEOUT
    ["i==3"] -> off/really_off
    [else] -> off/not_really_off/what
  what
    @OTHER -> ../on
''', '../../../off', 'not_really_off')]


@pytest.mark.parametrize('input, target, state', invalid_target_path_params)
def test_invalid_target_path(input, target, state):
    with pytest.raises(DefinitionError) as exc:
        parse(input)
    assert 'target path "{}" in state "{}" is invalid'.format(
        target, state) in str(exc.value)


def test_composite_state_names_not_unique():
    input = '''
/some_name
off
  @BUTTON_PRESS -> on
  @TIMEOUT -> off
  not_really_off
    @SOME_EVENT -> ../off
    @EVENT -> really_off
    @THIRD_EVENT -> not_really_off/what
    what
  really_off
    @OTHER_EVENT -> ../on/what
  not_really_off
    @OTHER -> ../on
on
  @TIMEOUT
    ["i==3"] -> off/really_off
    [else] -> off/not_really_off/what
  what
    @OTHER -> ../on
'''
    with pytest.raises(DefinitionError) as exc:
        parse(input)
    assert 'state name not unique in state "off"' in str(exc.value)


def test_composite_unreachable_state():
    input = '''
/some_name
off
  @BUTTON_PRESS -> on
  @TIMEOUT -> off
  not_really_off
    @SOME_EVENT -> ../off
    @THIRD_EVENT -> not_really_off/what
    what
  really_off
    @OTHER_EVENT -> ../on/what
on
  @TIMEOUT
    ["i==3"] -> on/what
    [else] -> off/not_really_off/what
  what
    @OTHER -> ../off
'''
    with pytest.raises(DefinitionError) as exc:
        parse(input)
    assert 'state "really_off" is unreachable' in str(exc.value)


def test_composite_reachable_state():
    input = '''
/some_name
off
  @BUTTON_PRESS -> on
  @TIMEOUT -> off
  not_really_off
    @SOME_EVENT -> ../off
    @THIRD_EVENT -> not_really_off/what
    what
  really_off
    @OTHER_EVENT -> ../on/what
on
  @TIMEOUT
    ["i==3"] -> on/what
    [else] -> off/not_really_off/what
  what
    @OTHER -> ../off/really_off
'''
    parse(input)


def test_comments():
    input = '''
// comment 0
/some_name
// comment 1
off
  @BUTTON_PRESS -> on // comment 2
  @TIMEOUT -> off
    // comment 3
  not_really_off
  // comment 4
    @SOME_EVENT -> ../off
    @THIRD_EVENT -> not_really_off/what // comment 5
    what
  really_off
    @OTHER_EVENT -> ../on/what
on
  @TIMEOUT
    ["i==3"] -> on/what
    [else] -> off/not_really_off/what
  what
    @OTHER -> ../off/really_off

 // comment 6
// comment 7
'''
    parse(input)
