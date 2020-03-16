from collections import OrderedDict
from lark import Lark, Transformer, v_args
from lark.indenter import Indenter
from lark.exceptions import LarkError
from .state_chart import Transition, EventHandler, State
from .error import Error


class ParsingError(Error):
    def __str__(self):
        if self.__cause__ is None:
            return super().__str__()

        return self.__cause__.__str__()


class DefinitionError(Error):
    pass


class ScIndenter(Indenter):
    NL_type = '_NEWLINE'
    OPEN_PAREN_types = []
    CLOSE_PAREN_types = []
    INDENT_type = '_INDENT'
    DEDENT_type = '_DEDENT'
    tab_len = 2


class ScTransformer(Transformer):
    @v_args(inline=True)
    def start(self, state_name, attributes):
        return State(state_name, **attributes)

    @v_args(inline=True)
    def attributes(self, *attributes):
        return collect_attributes(attributes)

    @v_args(inline=True)
    def init(self, actions):
        return dict(init_actions=actions)

    @v_args(inline=True)
    def exit(self, actions):
        return dict(exit_actions=actions)

    @v_args(inline=True)
    def event_handler(self, handler):
        return handler

    @v_args(inline=True)
    def state(self, state):
        return state

    @v_args(inline=True)
    def actions(self, *actions):
        return list(actions)

    @v_args(inline=True)
    def unguarded_event_handler(self, event, target):
        return EventHandler(event, transitions=[Transition(**target)])

    @v_args(inline=True)
    def guarded_event_handler(self, event, *transitions):
        return EventHandler(event, transitions=transitions)

    @v_args(inline=True)
    def regular_state(self, state_name, *attributes):
        return State(state_name, **(attributes[0]) if attributes else {})

    @v_args(inline=True)
    def transient_state(self, state_name, *transitions):
        return State(
            state_name,
            event_handlers=[EventHandler(None, transitions=transitions)])

    @v_args(inline=True)
    def event(self, event_name):
        return event_name

    @v_args(inline=True)
    def target(self, target_):
        return target_

    @v_args(inline=True)
    def external_target(self, state_path, *actions):
        return dict(target=state_path, actions=actions[0] if actions else [])

    @v_args(inline=True)
    def internal_target(self, actions):
        return dict(target=None, actions=actions)

    @v_args(inline=True)
    def guarded_transition(self, guard, target):
        target['guard'] = guard
        return Transition(**target)

    @v_args(inline=True)
    def else_transition(self, target):
        target['guard'] = Transition.else_guard
        return Transition(**target)

    @v_args(inline=True)
    def transient_guarded_transition(self, guard, target):
        target['guard'] = guard
        return Transition(**target)

    @v_args(inline=True)
    def transient_else_transition(self, target):
        target['guard'] = Transition.else_guard
        return Transition(**target)

    @v_args(inline=True)
    def string_(self, name):
        return str(name)

    @v_args(inline=True)
    def escaped_string(self, string):
        return str(string).strip('"')

    state_name = string_
    event_name = string_
    action = escaped_string
    guard = escaped_string
    state_path = string_


def collect_attributes(attributes):
    dict_ = {}
    event_handlers = []
    states = []
    for attr in attributes:
        if isinstance(attr, EventHandler):
            event_handlers.append(attr)
        elif isinstance(attr, dict):
            dict_.update(attr)
        elif isinstance(attr, State):
            states.append(attr)
        else:
            print(type(attr), attr)
            assert False
    dict_['event_handlers'] = event_handlers
    dict_['states'] = states
    return dict_


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


def get_state_paths(root_state):
    paths = OrderedDict()
    for state in root_state.all_states:
        paths[state.path] = state
    return paths


def validate_states_are_reachable(states):
    # all states are reachable
    # if all atomic states are reachable
    # either by being the transition target of a reachable state
    # or by being the initial state of a reachable state
    assert len(states) > 0

    def next_(srcs):
        dests = []
        for src in srcs:
            for transition in src.transitions:
                if transition.target is not None and transition.target not in reachables:
                    dests.append(transition.target)
            if not src.is_atomic and src.initial not in reachables:
                dests.append(src.initial)
        return dests

    srcs = [next(iter(states))]
    reachables = set(srcs)
    while len(srcs) > 0:
        srcs = next_(srcs)
        reachables.update(srcs)

    for substate in states:
        if substate.is_atomic and substate not in reachables:
            raise DefinitionError('state "{}" is unreachable'.format(
                substate.name))


def validate_states_names(state):
    if not unique([state.name for state in state.states]):
        raise DefinitionError('state name not unique in state "{}"'.format(
            state.name))


def validate_event_names(state):
    event_names = [
        event_handler.event for event_handler in state.event_handlers
    ]
    if not unique(event_names):
        raise DefinitionError('event handler not unique in state "{}"'.format(
            state.name))


def validate_guards(event_handler):
    guards = [transition.guard for transition in event_handler.transitions]
    if not unique(guards):
        raise DefinitionError('guard not unique for event "{}"'.format(
            event_handler.event))


def validate_target_path(transition):
    if transition.target is None:
        return transition.state.path

    def raise_invalid():
        raise DefinitionError(
            'target path "{}" in state "{}" is invalid'.format(
                transition.target, transition.state.name))

    if transition.target.startswith('..'):
        if transition.state.is_root:
            raise_invalid()
        elements = transition.state.parent.path.split('/')
        target_elements = transition.target.split('/')
        for i, element in enumerate(target_elements):
            if element != '..':
                break
        if i > len(elements):
            raise_invalid()
        return '/'.join(elements[:-i] + target_elements[i:])

    prefix_path = transition.state.parent.path if not transition.state.is_root else ''
    return join(prefix_path, transition.target)


def validate(root_state):
    state_paths = get_state_paths(root_state)

    for state in state_paths.values():

        for event_handler in state.event_handlers:
            validate_guards(event_handler)

            for transition in event_handler.transitions:
                target_path = validate_target_path(transition)
                target_state = state_paths.get(target_path)
                if target_state is None:
                    raise DefinitionError(
                        'invalid transition target "{}" in state "{}"'.format(
                            transition.target, state.name))
                # internal transition mean target is None
                if transition.target is not None:
                    transition.target = target_state

        validate_states_names(state)
        validate_event_names(state)

    validate_states_are_reachable(state_paths.values())


def parse(input_):
    try:
        parser = Lark.open('state_chart.lark',
                           rel_to=__file__,
                           parser='lalr',
                           postlex=ScIndenter())
        # all rules expect a newline at the end
        # we just automatically add one at the end of the input
        # in case the user hasn't added it
        tree = parser.parse(input_ + '\n')
        root_state = ScTransformer().transform(tree)
        validate(root_state)
        return root_state
    except LarkError as exc:
        raise ParsingError from exc
