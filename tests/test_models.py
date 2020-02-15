import pytest
import os
import scgen
import schematics

current_dir = os.path.dirname(__file__)


def local(file_name):
    return os.path.join(current_dir, file_name)


def test_simplest():
    with open(local('simplest.yaml'), 'r') as f:
        simplest = scgen.load(f)
    assert len(simplest.states) == 2
    assert simplest.states[0].name == "Occupied"
    assert simplest.states[0].transitions[0].event == "PIR_HIT"


def test_none():
    with pytest.raises(scgen.LoadingError):
        scgen.load(None)


def test_garbage():
    with pytest.raises(scgen.LoadingError):
        scgen.load("garbage")


def test_state_no_name():
    with open(local('no_name.yaml'), 'r') as f:
        with pytest.raises(scgen.LoadingError) as exc:
            scgen.load(f)
    cause = exc.value.__cause__
    assert type(cause) is schematics.exceptions.DataError


def test_state_names_not_unique():
    with open(local('names_not_unique.yaml'), 'r') as f:
        with pytest.raises(scgen.LoadingError) as exc:
            scgen.load(f)
    cause = exc.value.__cause__
    assert 'unique' in str(cause)


def test_invalid_transition_target_name():
    with open(local('invalid_transition_target_name.yaml'), 'r') as f:
        with pytest.raises(scgen.LoadingError) as exc:
            scgen.load(f)
    cause = exc.value.__cause__
    assert 'invalid transition target name' in str(cause)


def test_invalid_transition_event():
    with open(local('invalid_transition_event.yaml'), 'r') as f:
        with pytest.raises(scgen.LoadingError) as exc:
            scgen.load(f)
    cause = exc.value.__cause__
    assert 'transition events must be unique' in str(cause)


def test_unreachable_state():
    with open(local('unreachable_state.yaml'), 'r') as f:
        with pytest.raises(scgen.LoadingError) as exc:
            scgen.load(f)
    cause = exc.value.__cause__
    assert 'unreachable' in str(cause)
