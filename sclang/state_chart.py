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


def validate_guards(event, transitions):
    guards = [transition.guard for transition in transitions]
    if not unique(guards):
        raise DefinitionError(
            'guards are not unique for event "{}"'.format(event))


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


def validate_event_names(name, event_handlers):
    if not unique([event_handler.event for event_handler in event_handlers]):
        raise DefinitionError('events not unique in state "{}"'.format(name))


class StateChart(object):
    def __init__(self, states):
        validate_states_names(states)
        validate_transitions_targets(states)
        validate_states_are_reachable(states)

        self.states = states

    def get_event_names(self):
        events = set()
        for state in self.states:
            for event_handler in state.event_handlers:
                events.add(event_handler.event)
        return events


class State(object):
    def __init__(self, name, event_handlers=[]):
        validate_event_names(name, event_handlers)
        self.name = name
        self.event_handlers = event_handlers

    @property
    def transitions(self):
        transitions = []
        for event_handler in self.event_handlers:
            transitions.extend(event_handler.transitions)
        return transitions


class EventHandler(object):
    def __init__(self, event, transitions):
        validate_guards(event, transitions)
        self.event = event
        self.transitions = transitions


class Transition(object):
    else_guard = object()

    def __init__(self, target, guard=None, action=None):
        self.target = target
        self.guard = guard
        self.action = action

    def has_else_guard(self):
        return self.guard is Transition.else_guard
