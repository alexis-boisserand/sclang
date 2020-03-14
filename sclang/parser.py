from lark import Lark, Transformer, v_args
from lark.indenter import Indenter
from lark.exceptions import LarkError
from .state_chart import Transition, EventHandler, State
from .error import Error, DefinitionError


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


class ParsingError(Error):
    def __str__(self):
        if self.__cause__ is None:
            return super().__str__()

        return self.__cause__.__str__()


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
    def state(self, state_name, *attributes):
        return State(state_name, **(attributes[0]) if attributes else {})

    @v_args(inline=True)
    def unguarded_event_handler(self, event, target):
        return EventHandler(event, transitions=[Transition(**target)])

    @v_args(inline=True)
    def guarded_event_handler(self, event, *transitions):
        return EventHandler(event, transitions=transitions)

    @v_args(inline=True)
    def guarded_transition(self, guard, target):
        target['guard'] = guard
        return Transition(**target)

    @v_args(inline=True)
    def else_transition(self, target):
        target['guard'] = Transition.else_guard
        return Transition(**target)

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
    def actions(self, *actions):
        return list(actions)

    def event(self, children):
        return None if len(children) == 0 else children[0]

    @v_args(inline=True)
    def string_(self, name):
        return str(name)

    @v_args(inline=True)
    def escaped_string(self, string):
        return str(string).strip('"')

    action = escaped_string
    guard = escaped_string
    state_name = string_
    event_name = string_
    state_path = string_


def validate_transitions_targets(root_state):
    sp = State.state_paths(root_state)
    for state in sp.values():
        for transition in state.transitions:
            if transition.target_path not in sp.keys():
                raise DefinitionError(
                    'invalid transition target "{}" in state "{}"'.format(
                        transition.target, state.name))


def validate_states_are_reachable(root_state):
    # all states are reachable
    # if all atomic states are reachable
    # either by being the transition target of a reachable state
    # or by being the initial state of a reachable state
    sp = State.state_paths(root_state)
    assert len(sp) > 0

    def next_(srcs):
        dests = []
        for src in srcs:
            for transition in src.transitions:
                dest = sp[transition.target_path]
                if dest not in reachables:
                    dests.append(dest)
            if not src.is_atomic and src.initial not in reachables:
                dests.append(src.initial)
        return dests

    srcs = [root_state.initial]
    reachables = set(srcs)
    while len(srcs) > 0:
        srcs = next_(srcs)
        reachables.update(srcs)

    for substate in sp.values():
        if substate.is_atomic and substate not in reachables:
            raise DefinitionError('state "{}" is unreachable'.format(
                substate.name))


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
        validate_transitions_targets(root_state)
        validate_states_are_reachable(root_state)
        return root_state
    except LarkError as exc:
        raise ParsingError from exc
