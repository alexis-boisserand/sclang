import itertools
from lark import Lark, Transformer, v_args
from lark.indenter import Indenter
from lark.exceptions import LarkError
from .state_chart import Transition, EventHandler, State, StateChart
from .error import Error

sc_grammar = r'''
    start: (_NL* state)+
    state: state_name _NL [_INDENT attribute* _DEDENT]

    attribute: event_handler | init | exit
    init: "@init" "/" action _NL
    exit: "@exit" "/" action _NL
    event_handler: eventless_handler | regular_event_handler

    regular_event_handler: event transitions
    eventless_handler: "_" transitions
    transitions: unguarded_transition | guarded_transitions

    unguarded_transition: target
    guarded_transitions: guarded_transition [_INDENT (guarded_transition)* else_transition? _DEDENT]
    guarded_transition: "[" guard "]" target
    else_transition: "[" "else" "]" target
    target: "->" state_path ("/" action)? _NL

    event: NAME
    state_path: NAME
    state_name: NAME
    guard: STRING
    action: STRING

    %import common.WS_INLINE
    %import common.ESCAPED_STRING -> STRING
    %declare _INDENT _DEDENT
    %ignore WS_INLINE

    _NL: /(\r?\n[\t ]*)+/

    NAME: LOWER_CASE | UPPER_CASE | CAMEL_CASE | LOWER_CAMEL_CASE
    LOWER_CASE: /([a-z]+_?)*[a-z]/
    UPPER_CASE: /([A-Z]+_?)*[A-Z]/
    CAMEL_CASE: /[A-Z][a-zA-Z]*/
    LOWER_CAMEL_CASE: /[a-z][a-zA-Z]*/
'''


class ParsingError(Error):
    def __str__(self):
        if self.__cause__ is None:
            return super().__str__()

        return self.__cause__.__str__()


class ScIndenter(Indenter):
    NL_type = '_NL'
    OPEN_PAREN_types = []
    CLOSE_PAREN_types = []
    INDENT_type = '_INDENT'
    DEDENT_type = '_DEDENT'
    tab_len = 2


class ScTransformer(Transformer):
    @v_args(inline=True)
    def start(self, *states):
        return StateChart(states)

    @v_args(inline=True)
    def state(self, state_name, *attribute):
        event_handlers = []
        for attr in attribute:
            if isinstance(attr, EventHandler):
                event_handlers.append(attr)
        return State(state_name, event_handlers)

    @v_args(inline=True)
    def attribute(self, attr):
        return attr

    def init(self, children):
        return None

    def exit(self, children):
        return None

    @v_args(inline=True)
    def event_handler(self, handler):
        return handler

    @v_args(inline=True)
    def regular_event_handler(self, event, transitions):
        return EventHandler(event, transitions=transitions)

    @v_args(inline=True)
    def eventless_handler(self, transitions):
        return EventHandler(None, transitions=transitions)

    @v_args(inline=True)
    def transitions(self, transitions):
        if isinstance(transitions, list):
            return transitions
        if isinstance(transitions, Transition):
            return [transitions]
        assert False

    def guarded_transitions(self, transitions):
        return transitions

    @v_args(inline=True)
    def unguarded_transition(self, target):
        return Transition(**target)

    @v_args(inline=True)
    def guarded_transition(self, guard, target):
        target['guard'] = guard
        return Transition(**target)

    @v_args(inline=True)
    def else_transition(self, target):
        target['guard'] = Transition.else_guard
        return Transition(**target)

    def target(self, children):
        if len(children) == 1:
            return dict(target=children[0])
        if len(children) == 2:
            return dict(target=children[0], action=children[1])
        assert False

    @v_args(inline=True)
    def string_(self, name):
        return str(name)

    @v_args(inline=True)
    def escaped_string(self, name):
        return str(name).strip('"')

    event = string_
    state_path = string_
    state_name = string_
    guard = escaped_string
    action = escaped_string


def parse(input_):
    try:
        parser = Lark(sc_grammar, parser='lalr', postlex=ScIndenter())
        tree = parser.parse(input_)
        return ScTransformer().transform(tree)
    except LarkError as exc:
        raise ParsingError from exc
