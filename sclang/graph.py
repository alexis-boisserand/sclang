import sys
import argparse
from graphviz import Digraph
from .parser import parse, ParsingError


def graph(state_chart):
    dot = Digraph()
    if state_chart.states:
        dot.node('entry', label='', shape='point')
    for state in state_chart.states:
        dot.node(state.name, label=state.name, shape='box', style='rounded')

    if state_chart.states:
        dot.edge('entry', state_chart.states[0].name)
    for state in state_chart.states:
        for transition in state.transitions:
            dot.edge(state.name, transition.target, label=transition.event)
    return dot


def main():
    parser = argparse.ArgumentParser(
        description='Generates the statechart representation.')
    parser.add_argument(
        '-d',
        '--dot',
        nargs='?',
        type=argparse.FileType('w'),
        const=sys.stdout,
        help=
        'Generates the graphviz dot file input. If no option is given, the file\'s content will be printed on the standard output.'
    )
    parser.add_argument('-sc',
                        '--state_chart',
                        required=True,
                        type=argparse.FileType('r'),
                        help='statechart declaration file')
    args = parser.parse_args()

    try:
        state_chart = parse(args.state_chart)
    except ParsingError as exc:
        print('Failed to load {}: {}'.format(args.state_chart.name, str(exc)))
        sys.exit(1)

    dot = graph(state_chart)
    if args.dot:
        args.dot.write(dot.source)
    dot.view()


if __name__ == '__main__':
    main()
