from lark import Lark, Transformer, v_args
from lark.indenter import Indenter
from .models import Transition, State, StateChart


sc_grammar = r'''
    start: (_NL* state)+
    state: state_name _NL [_INDENT transition* _DEDENT]

    transition: event? "->" state_path _NL

    event: NAME
    state_path: NAME
    state_name: NAME

    %import common.CNAME -> NAME
    %import common.WS_INLINE
    %declare _INDENT _DEDENT
    %ignore WS_INLINE

    _NL: /(\r?\n[\t ]*)+/
'''


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
    def state(self, state_name, *transitions):
        return State(state_name, transitions)

    def transition(self, args):
        if len(args) == 1:
            return Transition(args[0])

        if len(args) == 2:
            return Transition(args[1], args[0])

        assert False

    @v_args(inline=True)
    def to_str(self, name):
        return str(name)

    event = to_str
    state_path = to_str
    state_name = to_str


def parse(input_):
    parser = Lark(sc_grammar, parser='lalr', postlex=ScIndenter())
    tree = parser.parse(input_)
    return ScTransformer().transform(tree)
