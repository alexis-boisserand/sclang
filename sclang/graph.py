import os
import sys
import argparse
from jinja2 import Environment, FileSystemLoader
from .parser import parse, ParsingError

current_dir = os.path.dirname(__file__)
template_dir = os.path.join(current_dir, 'templates')


def make_event_label(event_handler, transition):
    event = '' if event_handler.event is None else event_handler.event
    if transition.has_else_guard():
        guard = '[else]'
    elif transition.guard is not None:
        guard = '[{}]'.format(transition.guard)
    else:
        guard = ''
    if transition.action is None:
        action = ''
    else:
        action = '/ {}'.format(transition.action)
    return '{} {} {}'.format(event, guard, action)


def graph(state_chart):
    env = Environment(loader=FileSystemLoader(template_dir),
                      trim_blocks=True,
                      lstrip_blocks=True)
    template = env.get_template('graph.jinja')
    template.stream(state_chart=state_chart).dump(sys.stdout)


def main():
    parser = argparse.ArgumentParser(
        description='Generates the statechart representation.')
    parser.add_argument('-sc',
                        '--state_chart',
                        required=True,
                        type=argparse.FileType('r'),
                        help='statechart declaration file')
    args = parser.parse_args()

    try:
        with args.state_chart:
            state_chart = parse(args.state_chart.read())
    except ParsingError as exc:
        print('Failed to load {}: {}'.format(args.state_chart.name, str(exc)))
        sys.exit(1)

    graph(state_chart)


if __name__ == '__main__':
    main()
