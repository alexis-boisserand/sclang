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
    parser = argparse.ArgumentParser(description='Generates FSM graph.')
    parser.add_argument('machine', type=argparse.FileType('r'))
    args = parser.parse_args()

    machine = load(args.machine)
    dot = graph(machine)
    print(dot.source)


if __name__ == '__main__':
    main()
