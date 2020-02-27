from pathlib import PurePosixPath
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


class StateBase(object):
    def __init__(self,
                 name,
                 event_handlers=[],
                 states=[],
                 init=None,
                 exit=None):
        validate_event_names(name, event_handlers)
        validate_states_names(states)
        validate_states_are_reachable(states)
        self.name = name
        self.event_handlers = event_handlers
        self.states = states
        self.init = init
        self.exit = exit

    @property
    def transitions(self):
        transitions = []
        for event_handler in self.event_handlers:
            transitions.extend(event_handler.transitions)
        return transitions

    @property
    def state_paths(self):
        paths = {self.name: self}
        for state in self.states:
            for path, substate in state.state_paths.items():
                new_path = str(PurePosixPath(self.name, path))
                paths[new_path] = substate
        return paths


class StateChart(StateBase):
    def __init__(self, event_handlers=[], states=[], init=None, exit=None):
        validate_transitions_targets(states)
        super().__init__('/', event_handlers, states, init, exit)

    @property
    def event_names(self):
        def event_names_(state):
            events = set()
            for substate in state.states:
                for event_handler in substate.event_handlers:
                    events.add(event_handler.event)
                events.update(event_names_(substate))
            return events

        return event_names_(self)


class State(StateBase):
    def __init__(self,
                 name,
                 event_handlers=[],
                 states=[],
                 init=None,
                 exit=None):
        super().__init__(name, event_handlers, states, init, exit)


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
