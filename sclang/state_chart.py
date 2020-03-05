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


def parent(abs_path):
    assert abs_path.startswith('/')
    elements = abs_path[1:].split('/')
    return '/' + '/'.join(elements[:-1])


def resolve(abs_path):
    assert abs_path.startswith('/')
    elements = abs_path[1:].split('/')
    new_elements = []
    for element in elements:
        if element == '..':
            try:
                new_elements.pop()
            except IndexError:
                raise DefinitionError('invalid path "{}"'.format(abs_path))
        else:
            new_elements.append(element)
    return '/' + '/'.join(new_elements)


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
        self._validate_event_names()
        self._validate_states_names()
        for state in self.states:
            state.parent = self
        for event_handler in self.event_handlers:
            event_handler.state = self
        for transition in self.transitions:
            transition.state = self


    @property
    def initial(self):
        assert self.parent and len(self.parent.states) > 0
        return self.parent is None or self.parent.states[0] is self

    @property
    def atomic(self):
        return len(self.states) == 0

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
            for path_, substate in state.state_paths.items():
                new_path = join(self.name, path_)
                paths[new_path] = substate
        return paths

    def _validate_event_names(self):
        event_names = [
            event_handler.event for event_handler in self.event_handlers
        ]
        if not unique(event_names):
            raise DefinitionError(
                'event handler not unique in state "{}"'.format(self.name))

    def _validate_states_names(self):
        if not unique([state.name for state in self.states]):
            raise DefinitionError('state name not unique in state "{}"'.format(
                self.name))


class StateChart(StateBase):
    def __init__(self, event_handlers=[], states=[], init=None, exit=None):
        super().__init__('/', event_handlers, states, init, exit)
        self.parent = None
        self._validate_transitions_targets()
        self._validate_states_are_reachable()

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
        state_paths = self.state_paths

        for path, state in state_paths.items():
            for transition in state.transitions:
                parent_path = parent(path)
                transition_path = resolve(join(parent_path, transition.target))
                if transition_path not in state_paths.keys():
                    raise DefinitionError(
                        'invalid transition target "{}" in state "{}"'.format(
                            transition.target, state.name))

        #states_names = [state.name for state in self.states]
        #for state in self.states:
        #    for transition in state.transitions:
        #        if transition.target not in states_names:
        #            raise DefinitionError(
        #                'invalid transition state path name "{}" in state "{}"'
        #                .format(transition.target, state.name))

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
        if self.target == '/':
            return '/'
        if self.target == '.':
            return self.state.path

    def has_else_guard(self):
        return self.guard is Transition.else_guard
