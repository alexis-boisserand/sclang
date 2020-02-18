import yaml
from schematics.models import Model
from schematics.types import ListType, ModelType
from schematics.exceptions import ValidationError
from .normalize import NormalizedStringType
from .errors import Error


class LoadingError(Error):
    def __str__(self):
        if self.__cause__:
            return str(self.__cause__)
        return super().__str__(self)


def unique_values(list_):
    set_ = set()
    for x in list_:
        if x in set_:
            return False
        set_.add(x)
    return True


def validate_states_names(states):
    if not unique_values([state.name for state in states]):
        raise ValidationError('states\' names must be unique')


def validate_transitions(states):
    states_names = [state.name for state in states]
    for state in states:
        for transition in state.transitions:
            if transition.target not in states_names:
                raise ValidationError(
                    'invalid transition target name "{}" in state "{}"'.format(
                        transition.target, state.name))


def validate_all_states_are_reachable(states):
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
    event = NormalizedStringType()
    target = NormalizedStringType(required=True)


class State(Model):
    name = NormalizedStringType(required=True)
    transitions = ListType(ModelType(Transition), required=True)

    def validate_transitions(self, data, transitions):
        event_names = [transition.event for transition in transitions]
        if not unique_values(event_names):
            raise ValidationError('transition events must be unique')


class StateChart(Model):
    name = NormalizedStringType(required=True)
    states = ListType(ModelType(State), required=True)

    def validate_states(self, data, states):
        validate_states_names(states)
        validate_transitions(states)
        validate_all_states_are_reachable(states)
        return states

    def list_event_names(self):
        events = set()
        for state in self.states:
            for transition in state.transitions:
                events.add(transition.event)
        return events


def load(stream):
    try:
        dict_ = yaml.safe_load(stream)
        state_chart = StateChart(dict_)
        state_chart.validate()
    except Exception as exc:
        raise LoadingError from exc
    return state_chart
