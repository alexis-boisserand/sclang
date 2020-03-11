from lark import Lark, Transformer, v_args
from lark.indenter import Indenter
from lark.exceptions import LarkError
from .state_chart import Transition, EventHandler, State, StateChart
from .error import Error

sc_grammar = r'''
    %import common.WS_INLINE
    %import common.ESCAPED_STRING -> STRING
    %declare _INDENT _DEDENT
    %ignore WS_INLINE
    %ignore COMMENT

    start: (_NEWLINE? state)+
    state: state_name _NEWLINE [_INDENT init? exit? event_handler* state* _DEDENT]

    init: "#init" _NEWLINE actions
    exit: "#exit" _NEWLINE actions
    event_handler: unguarded_event_handler
                 | guarded_event_handler

    unguarded_event_handler: event target
    guarded_event_handler: event _NEWLINE _INDENT guarded_transition+ else_transition? _DEDENT

    guarded_transition: "[" guard "]" target
    else_transition: "[" "else" "]" target

    target: "->" state_path _NEWLINE [actions]
    actions: _INDENT (action _NEWLINE)+ _DEDENT
    event: "@" ("_" | event_name)

    action: STRING
    guard: STRING
    state_name: NAME
    event_name: NAME
    state_path: STATE_PATH

    COMMENT: _NEWLINE? /\/\/.*/
    STATE_PATH: ("../")* (NAME"/")* NAME
    NAME: LOWER_CASE
        | CAMEL_CASE
        | UPPER_CASE
        | LOWER_CAMEL_CASE
    LOWER_CASE: /([a-z]+_?)*[a-z]/
    UPPER_CASE: /([A-Z]+_?)*[A-Z]/
    CAMEL_CASE: /([A-Z][a-z]+)+/
    LOWER_CAMEL_CASE: /([a-z]+[A-Z][a-z]+)+/
    _NEWLINE: /(\r?\n[\t ]*)+/
'''


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
    def start(self, *states):
        return StateChart(states=states)

    @v_args(inline=True)
    def state(self, state_name, *attributes):
        return State(state_name, **collect_attributes(attributes))

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
    def target(self, state_path, *actions):
        return dict(target=state_path, actions=actions[0] if actions else [])

    def event(self, children):
        return None if len(children) == 0 else children[0]

    @v_args(inline=True)
    def actions(self, *actions):
        return list(actions)

    @v_args(inline=True)
    def string_(self, name):
        return str(name)

    @v_args(inline=True)
    def escaped_string(self, str_):
        return str(str_).strip('"')

    action = escaped_string
    guard = escaped_string
    state_name = string_
    event_name = string_
    state_path = string_


def parse(input_):
    try:
        parser = Lark(sc_grammar, parser='lalr', postlex=ScIndenter())
        # all rules expect a newline at the end
        # we just automatically add one at the end of the input
        # in case the user hasn't added it
        tree = parser.parse(input_ + '\n')
        return ScTransformer().transform(tree)
    except LarkError as exc:
        raise ParsingError from exc
