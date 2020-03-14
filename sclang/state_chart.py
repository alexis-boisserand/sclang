from collections import OrderedDict
from cached_property import cached_property


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


class EventHandler(object):
    def __init__(self, event, transitions):
        self.event = event
        self.transitions = transitions
        for transition in self.transitions:
            transition.event_handler = self


class Transition(object):
    else_guard = object()

    def __init__(self, target, guard=None, actions=[]):
        self.target = target
        self.guard = guard
        self.actions = actions

    @cached_property
    def has_else_guard(self):
        return self.guard is Transition.else_guard
