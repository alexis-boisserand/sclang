from pathlib import PurePosixPath
from collections import OrderedDict
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


class StateBase(object):
    def __init__(self,
                 name,
                 event_handlers=[],
                 states=[],
                 init=None,
                 exit=None):
        self.name = name
        self.event_handlers = event_handlers
        self.states = states
        self.init = init
        self.exit = exit
        for state in self.states:
            state.parent = self
        self._validate_event_names()
        self._validate_states_names()
        self._validate_states_are_reachable()

    @property
    def path(self):
        elements = [self.name]
        parent = self.parent
        while parent.parent is not None:
            elements.append(parent.name)
            parent = parent.parent
        return '/' + '/'.join(reversed(elements))

    @property
    def transitions(self):
        transitions = []
        for event_handler in self.event_handlers:
            transitions.extend(event_handler.transitions)
        return transitions

    @property
    def state_paths(self):
        paths = OrderedDict()
        paths[self.name] = self
        for state in self.states:
            for path, substate in state.state_paths.items():
                new_path = str(PurePosixPath(self.name, path))
                paths[new_path] = substate
        return paths

    def _validate_event_names(self):
        event_names = [
            event_handler.event for event_handler in self.event_handlers
        ]
        if not unique(event_names):
            raise DefinitionError('events not unique in state "{}"'.format(
                self.name))

    def _validate_states_are_reachable(self):

        for dest in self.states[1:]:
            target_names = []
            for src in self.states:
                if src is not dest:
                    for transition in src.transitions:
                        target_names.append(transition.target)

            if dest.name not in target_names:
                raise DefinitionError('state "{}" is unreachable'.format(
                    dest.name))

    def _validate_states_names(self):
        if not unique([state.name for state in self.states]):
            raise DefinitionError('state names must be unique')


class StateChart(StateBase):
    def __init__(self, event_handlers=[], states=[], init=None, exit=None):
        super().__init__('/', event_handlers, states, init, exit)
        self.parent = None
        self._validate_transitions_targets()

    @property
    def path(self):
        return self.name

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

    def _validate_transitions_targets(self):
        states_names = [state.name for state in self.states]
        for state in self.states:
            for transition in state.transitions:
                if transition.target not in states_names:
                    raise DefinitionError(
                        'invalid transition target name "{}" in state "{}"'.
                        format(transition.target, state.name))


class State(StateBase):
    def __init__(self,
                 name,
                 event_handlers=[],
                 states=[],
                 init=None,
                 exit=None):
        assert name
        super().__init__(name, event_handlers, states, init, exit)


class EventHandler(object):
    def __init__(self, event, transitions):
        self.event = event
        self.transitions = transitions
        self._validate_guards()

    def _validate_guards(self):
        guards = [transition.guard for transition in self.transitions]
        if not unique(guards):
            raise DefinitionError(
                'guards are not unique for event "{}"'.format(self.event))


class Transition(object):
    else_guard = object()

    def __init__(self, target, guard=None, action=None):
        self.target = target
        self.guard = guard
        self.action = action

    def has_else_guard(self):
        return self.guard is Transition.else_guard
