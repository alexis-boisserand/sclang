import yaml
from schematics.models import Model
from schematics.types import StringType, ListType, ModelType
from schematics.exceptions import ValidationError
from .errors import LoadingError


def unique_values(list_):
    set_ = set()
    for x in list_:
        if x in set_:
            return False
        set_.add(x)
    return True


class Transition(Model):
    event = StringType(required=True)
    target = StringType(required=True)


class State(Model):
    name = StringType(required=True)
    transitions = ListType(ModelType(Transition), required=True)


class Machine(Model):
    states = ListType(ModelType(State), required=True)

    def validate_states(self, data, states):
        state_names = [state.name for state in states]
        if not unique_values(state_names):
            raise ValidationError('state names must be unique')

        for state in states:
            event_names = []
            for transition in state.transitions:
                if transition.target not in state_names:
                    raise ValidationError(
                        'invalid transition target name "{}" in state "{}"'.
                        format(transition.target, state.name))
                event_names.append(transition.event)

            if not unique_values(event_names):
                raise ValidationError(
                    'transition events must be unique for state "{}"'.format(
                        state.name))

        # check that all non-initial states have at least one predecessor
        for dest in states[1:]:
            target_names = []
            for src in states:
                if src is not dest:
                    for transition in src.transitions:
                        target_names.append(transition.target)

            if dest.name not in target_names:
                raise ValidationError('state "{}" is unreachable'.format(
                    dest.name))

        return states


def load(stream):
    try:
        dict_ = yaml.safe_load(stream)
        machine = Machine(dict_)
        machine.validate()
    except Exception as exc:
        raise LoadingError from exc
    return machine
