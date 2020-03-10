import os
import sys
import io
import argparse
from subprocess import Popen, PIPE, TimeoutExpired
from jinja2 import Environment, FileSystemLoader
from .parser import parse, ParsingError

current_dir = os.path.dirname(__file__)
template_dir = os.path.join(current_dir, 'templates')
plantuml_bin = os.path.join(current_dir, 'plantuml', 'plantuml.jar')


def add_unique_name_attr(state_chart):
    names = set()
    for state in state_chart.all_states:
        if state.name not in names:
            unique_name = state.name
        else:
            unique_name = state.name + '_'

        names.add(unique_name)
        state.unique_name = unique_name


def graph(state_chart):
    add_unique_name_attr(state_chart)
    env = Environment(loader=FileSystemLoader(template_dir),
                      trim_blocks=True,
                      lstrip_blocks=True)
    template = env.get_template('graph.jinja')
    with Popen(['java', '-jar', plantuml_bin, '-p'], stdin=PIPE,
               stdout=PIPE) as proc:
        template.stream(state_chart=state_chart).dump(proc.stdin,
                                                      encoding='utf-8')
        proc.stdin.close()
        return proc.stdout.read()


def main():
    parser = argparse.ArgumentParser(
        description='Generates the statechart representation.')
    parser.add_argument('state_chart',
                        type=argparse.FileType('r'),
                        help='statechart declaration file')
    parser.add_argument('-o',
                        '--output',
                        type=argparse.FileType('wb'),
                        help='output file name')
    args = parser.parse_args()

    try:
        with args.state_chart:
            state_chart = parse(args.state_chart.read())
    except ParsingError as exc:
        print('Failed to load {}: {}'.format(args.state_chart.name, str(exc)))
        sys.exit(1)

    if args.output:
        output = args.output
    else:
        base = os.path.splitext(os.path.basename(args.state_chart.name))[0]
        output_name = base + '.png'
        output = open(output_name, 'wb')
    with output:
        output.write(graph(state_chart))


if __name__ == '__main__':
    main()
