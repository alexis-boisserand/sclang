import os
import sys
import argparse
from jinja2 import Environment, FileSystemLoader
from .parser import parse, ParsingError

current_dir = os.path.dirname(__file__)
template_dir = os.path.join(current_dir, 'templates')


def graph(state_chart):
    env = Environment(loader=FileSystemLoader(template_dir),
                      trim_blocks=True,
                      lstrip_blocks=True)
    template = env.get_template('graph.jinja')
    template.stream(state_chart=state_chart).dump(sys.stdout)


def main():
    parser = argparse.ArgumentParser(
        description='Generates the statechart representation.')
    parser.add_argument('state_chart',
                        type=argparse.FileType('r'),
                        help='statechart declaration file')
    args = parser.parse_args()

    try:
        with args.state_chart:
            state_chart = parse(args.state_chart.read())
            for k, v in state_chart.state_paths.items():
                print(k, v.name)
                for transition in v.transitions:
                    print(transition.target)
    except ParsingError as exc:
        print('Failed to load {}: {}'.format(args.state_chart.name, str(exc)))
        sys.exit(1)

    graph(state_chart)


if __name__ == '__main__':
    main()
