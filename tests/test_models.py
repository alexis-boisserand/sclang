import os
import pytest
import scgen
import schematics

current_dir = os.path.dirname(__file__)


def local(file_name):
    return os.path.join(current_dir, file_name)


def remove_prefix(text, prefix):
    return text[text.startswith(prefix) and len(prefix):]


@pytest.fixture(scope='function')
def input_file(request):
    basename = remove_prefix(request.function.__name__, 'test_')
    name = os.path.join('models', '{}.yaml'.format(basename))
    with open(local(name), 'r') as f:
        yield f


def test_simplest(input_file):
    sc = scgen.load(input_file)
    assert len(sc.states) == 2
    assert sc.states[0].name == 'Off'
    assert sc.states[0].transitions[0].event == 'BUTTON_PRESS'


def test_none():
    with pytest.raises(scgen.LoadingError):
        scgen.load(None)


def test_garbage():
    with pytest.raises(scgen.LoadingError):
        scgen.load('garbage')


def test_state_no_name(input_file):
    with pytest.raises(scgen.LoadingError) as exc:
        scgen.load(input_file)
    cause = exc.value.__cause__
    assert type(cause) is schematics.exceptions.DataError


def test_empty_name(input_file):
    with pytest.raises(scgen.LoadingError) as exc:
        scgen.load(input_file)
    cause = exc.value.__cause__
    assert type(cause) is schematics.exceptions.DataError


def test_state_names_not_unique(input_file):
    with pytest.raises(scgen.LoadingError) as exc:
        scgen.load(input_file)
    cause = exc.value.__cause__
    assert 'unique' in str(cause)


def test_invalid_transition_target_name(input_file):
    with pytest.raises(scgen.LoadingError) as exc:
        scgen.load(input_file)
    cause = exc.value.__cause__
    assert 'invalid transition target name' in str(cause)


def test_transition_events_not_unique(input_file):
    with pytest.raises(scgen.LoadingError) as exc:
        scgen.load(input_file)
    cause = exc.value.__cause__
    assert 'transition events must be unique' in str(cause)


def test_unreachable_state(input_file):
    with pytest.raises(scgen.LoadingError) as exc:
        scgen.load(input_file)
    cause = exc.value.__cause__
    assert 'unreachable' in str(cause)


def test_eventless_transition(input_file):
    sc = scgen.load(input_file)
    assert sc.states[1].transitions[0].event is None


def test_eventless_transitions_not_unique(input_file):
    with pytest.raises(scgen.LoadingError) as exc:
        scgen.load(input_file)
    cause = exc.value.__cause__
    assert 'transition events must be unique' in str(cause)


def test_guard(input_file):
    sc = scgen.load(input_file)
    assert sc.states[1].transitions[0].guard == "i < 3"