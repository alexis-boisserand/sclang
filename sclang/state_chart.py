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


def join(path1, path2):
    assert (path1 == '/' or not path1.endswith('/')
            ) and not path2.endswith('/') and not path2.startswith('/')
    if path1 == '/':
        return path1 + path2
    return path1 + '/' + path2


class StateBase(object):
    def __init__(self, name, states=[]):
        self.name = name
        self.states = states
        for state in self.states:
            state.parent = self
        self._validate_states_names()

    def _validate_states_names(self):
        if not unique([state.name for state in self.states]):
            raise DefinitionError('state name not unique in state "{}"'.format(
                self.name))


class StateChart(StateBase):
    def __init__(self, states=[]):
        super().__init__('/', states)
        self._validate_transitions_targets()
        self._validate_states_are_reachable()

    @property
    def state_paths(self):
        def _state_paths(state):
            paths = OrderedDict()
            if state.name != '/':
                paths[state.name] = state
            for state_ in state.states:
                for path_, substate in _state_paths(state_).items():
                    new_path = join(state.name, path_)
                    paths[new_path] = substate
            return paths

        return _state_paths(self)

    @property
    def event_names(self):
        def _event_names(state):
            events = set()
            for substate in state.states:
                for event_handler in substate.event_handlers:
                    events.add(event_handler.event)
                events.update(_event_names(substate))
            return events

        return _event_names(self)

    def _validate_transitions_targets(self):
        state_paths = self.state_paths
        for state in state_paths.values():
            for transition in state.transitions:
                if transition.target_path not in state_paths.keys():
                    raise DefinitionError(
                        'invalid transition target "{}" in state "{}"'.format(
                            transition.target, state.name))

    def _validate_states_are_reachable(self):
        # all states are reachable
        # if all atomic states are reachable
        # either by being the transition target of a reachable state
        # or by being the initial state of a reachable state
        state_paths = self.state_paths
        assert len(state_paths) > 0

        def next_(srcs):
            dests = []
            for src in srcs:
                for transition in src.transitions:
                    dest = state_paths[transition.target_path]
                    if dest not in reachables:
                        dests.append(dest)
                if not src.is_atomic and src.initial not in reachables:
                    dests.append(src.initial)
            return dests

        srcs = [self.states[0]]
        reachables = set(srcs)
        while len(srcs) > 0:
            srcs = next_(srcs)
            reachables.update(srcs)

        for state in state_paths.values():
            if state.is_atomic and state not in reachables:
                raise DefinitionError('state "{}" is unreachable'.format(
                    state.name))


class State(StateBase):
    def __init__(self,
                 name,
                 event_handlers=[],
                 states=[],
                 init=None,
                 exit=None):
        super().__init__(name, states)
        self.event_handlers = event_handlers
        self.init = init
        self.exit = exit
        for event_handler in self.event_handlers:
            event_handler.state = self
        for transition in self.transitions:
            transition.state = self
        self._validate_event_names()

    @property
    def path(self):
        elements = [self.name]
        state = self
        while not state.is_root:
            elements.append(state.parent.name)
            state = state.parent
        return '/' + '/'.join(reversed(elements))

    @property
    def transitions(self):
        transitions = []
        for event_handler in self.event_handlers:
            transitions.extend(event_handler.transitions)
        return transitions

    @property
    def is_root(self):
        return isinstance(self.parent, StateChart)

    @property
    def is_initial(self):
        return self.parent.states[0] is self

    @property
    def initial(self):
        assert not self.is_atomic
        return self.states[0]

    @property
    def is_atomic(self):
        return len(self.states) == 0

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

    def __init__(self, target, guard=None, action=None):
        self.target = target
        self.guard = guard
        self.action = action

    @property
    def target_path(self):
        def raise_invalid():
            raise DefinitionError(
                'target path "{}" in state "{}" is invalid'.format(
                    self.target, self.state.name))

        if self.target.startswith('..'):
            if self.state.is_root:
                raise_invalid()
            elements = self.state.parent.path.lstrip('/').split('/')
            target_elements = self.target.split('/')
            for i, element in enumerate(target_elements):
                if element != '..':
                    break
            if i > len(elements):
                raise_invalid()
            return '/' + '/'.join(elements[:-i] + target_elements[i:])

        prefix_path = self.state.parent.path if not self.state.is_root else '/'
        return join(prefix_path, self.target)

    def has_else_guard(self):
        return self.guard is Transition.else_guard
