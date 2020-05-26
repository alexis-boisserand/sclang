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
    def path_elements(self):
        return self.path.split('/')

    @cached_property
    def all_states(self):
        states = [self]
        for state in self.states:
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
    def is_transient(self):
        return len(
            self.event_handlers) == 1 and self.event_handlers[0].event is None

    @cached_property
    def initial(self):
        assert not self.is_atomic
        return self.states[0]

    @cached_property
    def is_atomic(self):
        return len(self.states) == 0

    @cached_property
    def event_names(self):
        events = set()
        for event_handler in self.event_handlers:
            if event_handler.event is not None:
                events.add(event_handler.event)
        for substate in self.states:
            events.update(substate.event_names)
        return events

    @cached_property
    def state_paths(self):
        if self.parent is None:
            paths = OrderedDict()
            for state in self.all_states:
                paths[state.path] = state
            return paths
        state = self.parent
        while state.parent is not None:
            state = state.parent
        return state.state_paths

    def common_ancestor(self, other):
        elts = self.path_elements
        other_elts = other.path_elements
        common_elts = []
        for elt, other_elt in zip(elts, other_elts):
            if elt == other_elt:
                common_elts.append(elt)
            else:
                break
        return self.state_paths['/'.join(common_elts)]

    def states_to_ancestor(self, ancestor):
        if self is ancestor:
            return []
        parent = self.parent
        states = []
        while parent not in [None, ancestor]:
            states.append(parent)
            parent = parent.parent
        return states


class EventHandler:
    def __init__(self, event, transitions):
        self.event = event
        self.transitions = transitions
        for transition in self.transitions:
            transition.event_handler = self

    @cached_property
    def is_unguarded(self):
        return len(self.transitions) == 1 and self.transitions[0].guard is None


class Transition:
    else_guard = object()

    def __init__(self, target, guard=None, actions=[]):
        self.target = target
        self.guard = guard
        self.actions = actions

    @cached_property
    def is_else_guard(self):
        return self.guard is Transition.else_guard

    @property
    def is_internal(self):
        return self.target is None
