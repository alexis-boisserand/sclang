from collections import OrderedDict
from cached_property import cached_property
from .error import DefinitionError



def unique(list_):
    set_ = set()
    for x in list_:
        if x in set_:
            return False
        set_.add(x)
    return True


def join(path1, path2):
    if path1 == '':
        return path1 + path2
    return path1 + '/' + path2


class State:
    def __init__(self,
                 name,
                 event_handlers=[],
                 states=[],
                 init_actions=[],
                 exit_actions=[]):
        self.name = name
        self.states = states
        self.event_handlers = event_handlers
        self.init_actions = init_actions
        self.exit_actions = exit_actions
        self.parent = None

        for state in self.states:
            state.parent = self
        for event_handler in self.event_handlers:
            event_handler.state = self
        for transition in self.transitions:
            transition.state = self

        self._validate_states_names()
        self._validate_event_names()

    @cached_property
    def path(self):
        elements = []
        state = self
        while not state.is_root:
            elements.append(state.name)
            state = state.parent
        elements.append(state.name)
        return '/'.join(reversed(elements))

    @cached_property
    def all_states(self):
        states = []
        for state in self.states:
            states.append(state)
            states.extend(state.all_states)
        return states

    @cached_property
    def transitions(self):
        transitions = []
        for event_handler in self.event_handlers:
            transitions.extend(event_handler.transitions)
        return transitions

    @cached_property
    def is_root(self):
        return self.parent is None

    @cached_property
    def is_initial(self):
        if self.is_root:
            return True
        return self.parent.states[0] is self

    @cached_property
    def initial(self):
        assert not self.is_atomic
        return self.states[0]

    @cached_property
    def is_atomic(self):
        return len(self.states) == 0

    @staticmethod
    def state_paths(root_state):
        paths = OrderedDict()
        paths[root_state.path] = root_state
        for state in root_state.all_states:
            paths[state.path] = state
        return paths

    @staticmethod
    def event_names(root_state):
        def _event_names(state):
            events = set()
            for event_handler in state.event_handlers:
                events.add(event_handler.event)
            for substate in state.states:
                events.update(_event_names(substate))
            return events

        return _event_names(root_state)

    def _validate_states_names(self):
        if not unique([state.name for state in self.states]):
            raise DefinitionError('state name not unique in state "{}"'.format(
                self.name))

    def _validate_event_names(self):
        event_names = [
            event_handler.event for event_handler in self.event_handlers
        ]
        if not unique(event_names):
            raise DefinitionError(
                'event handler not unique in state "{}"'.format(self.name))


class EventHandler(object):
    def __init__(self, event, transitions):
        self.event = event
        self.transitions = transitions
        for transition in self.transitions:
            transition.event_handler = self
        self._validate_guards()

    def _validate_guards(self):
        guards = [transition.guard for transition in self.transitions]
        if not unique(guards):
            raise DefinitionError('guard not unique for event "{}"'.format(
                self.event))


class Transition(object):
    else_guard = object()

    def __init__(self, target, guard=None, actions=[]):
        self.target = target
        self.guard = guard
        self.actions = actions

    @cached_property
    def is_internal(self):
        return self.target is None

    @cached_property
    def target_path(self):
        if self.is_internal:
            return self.state.path

        def raise_invalid():
            raise DefinitionError(
                'target path "{}" in state "{}" is invalid'.format(
                    self.target, self.state.name))

        if self.target.startswith('..'):
            if self.state.is_root:
                raise_invalid()
            elements = self.state.parent.path.split('/')
            target_elements = self.target.split('/')
            for i, element in enumerate(target_elements):
                if element != '..':
                    break
            if i > len(elements):
                raise_invalid()
            return '/'.join(elements[:-i] + target_elements[i:])

        prefix_path = self.state.parent.path if not self.state.is_root else ''
        return join(prefix_path, self.target)

    @cached_property
    def has_else_guard(self):
        return self.guard is Transition.else_guard
