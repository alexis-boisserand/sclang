import sys
import argparse
from graphviz import Digraph
from .models import load


def graph(machine):
    dot = Digraph()
    if machine.states:
        dot.node('entry', shape='point', label='')
    for state in machine.states:
        dot.node(state.name, state.name)

    if machine.states:
        dot.edge('entry', machine.states[0].name)
    for state in machine.states:
        for transition in state.transitions:
            dot.edge(state.name, transition.target, label=transition.event)
    return dot


def main():
    parser = argparse.ArgumentParser(description='Generates an FSM graph.')
    parser.add_argument(
        '-d',
        '--dot',
        nargs='?',
        type=argparse.FileType('w'),
        const=sys.stdout,
        help=
        'Generates the graphviz dot file input. If no option is given, the file\'s content will be printed on the standard output.'
    )
    parser.add_argument(
        '-m',
        '--machine',
        required=True,
        type=argparse.FileType('r'),
        help='FSM declaration file')
    args = parser.parse_args()

    machine = load(args.machine)
    dot = graph(machine)
    if args.dot:
        args.dot.write(dot.source)
    dot.view()

if __name__ == '__main__':
    main()
