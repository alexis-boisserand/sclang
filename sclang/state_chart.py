from .error import Error


class DefinitionError(Error):
    pass


def unique(list_):
    set_ = set()
    for x in list_:
        if x in set_:
            return False
        set_.add(x)
    return True


def validate_states_names(states):
    if not unique([state.name for state in states]):
        raise DefinitionError('state names must be unique')


def validate_transitions_targets(states):
    states_names = [state.name for state in states]
    for state in states:
        for transition in state.transitions:
            if transition.target not in states_names:
                raise DefinitionError(
                    'invalid transition target name "{}" in state "{}"'.format(
                        transition.target, state.name))


def validate_states_are_reachable(states):
    for dest in states[1:]:
        target_names = []
        for src in states:
            if src is not dest:
                for transition in src.transitions:
                    target_names.append(transition.target)

        if dest.name not in target_names:
            raise DefinitionError('state "{}" is unreachable'.format(
                dest.name))


class StateChart(object):
    def __init__(self, states):
        validate_states_names(states)
        validate_transitions_targets(states)
        validate_states_are_reachable(states)

        self.states = states

    def get_event_names(self):
        events = set()
        for state in self.states:
            for transition in state.transitions:
                events.add(transition.event)
        return events


class State(object):
    def __init__(self, name, transitions):
        if not unique([transition.event for transition in transitions]):
            raise DefinitionError(
                'conflicts between at least two transitions in state "{}"'.
                format(name))

        self.name = name
        self.transitions = transitions


class Transition(object):
    def __init__(self, target, event=None):
        self.target = target
        self.event = event
