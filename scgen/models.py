import yaml
from schematics.models import Model
from schematics.types import StringType, ListType, ModelType
from schematics.exceptions import ValidationError
from .errors import Error


class LoadingError(Error):
    def __str__(self):
        if self.__cause__:
            return str(self.__cause__)
        return super().__str__(self)


def _unique_values(list_):
    set_ = set()
    for x in list_:
        if x in set_:
            return False
        set_.add(x)
    return True


def _validate_states_names(states):
    if not _unique_values([state.name for state in states]):
        raise ValidationError('states\' names must be unique')


def _validate_transitions(states):
    states_names = [state.name for state in states]
    for state in states:
        for transition in state.transitions:
            if transition.target not in states_names:
                raise ValidationError(
                    'invalid transition target name "{}" in state "{}"'.format(
                        transition.target, state.name))


def _validate_all_states_are_reachable(states):
    for dest in states[1:]:
        target_names = []
        for src in states:
            if src is not dest:
                for transition in src.transitions:
                    target_names.append(transition.target)

        if dest.name not in target_names:
            raise ValidationError('state "{}" is unreachable'.format(
                dest.name))


class Transition(Model):
    event = StringType(required=True)
    target = StringType(required=True)


class State(Model):
    name = StringType(required=True)
    transitions = ListType(ModelType(Transition), required=True)

    def validate_transitions(self, data, transitions):
        event_names = [transition.event for transition in transitions]
        if not _unique_values(event_names):
            raise ValidationError('transition events must be unique')


class Machine(Model):
    name = StringType(required=True)
    states = ListType(ModelType(State), required=True)

    def validate_states(self, data, states):
        _validate_states_names(states)
        _validate_transitions(states)
        _validate_all_states_are_reachable(states)

        return states


def load(stream):
    try:
        dict_ = yaml.safe_load(stream)
        machine = Machine(dict_)
        machine.validate()
    except Exception as exc:
        raise LoadingError from exc
    return machine
