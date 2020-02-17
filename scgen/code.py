import os
import sys
import argparse
from jinja2 import Environment, FileSystemLoader
from .models import load, LoadingError
from .normalize import upper_case, lower_case, camel_case

current_dir = os.path.dirname(__file__)


def code(state_chart, output_dir):
    template_dir = os.path.join(current_dir, 'templates')
    filters = {
        func.__name__: func
        for func in [upper_case, lower_case, camel_case]
    }
    env = Environment(loader=FileSystemLoader(template_dir),
                      trim_blocks=True,
                      lstrip_blocks=True)
    env.filters.update(filters)
    inputs = [('state_chart_header.jinja', 'h'),
              ('state_chart_impl.jinja', 'c')]
    file_prefix = lower_case(state_chart.name)
    for input_, ext in inputs:
        template = env.get_template(input_)
        output = os.path.join(output_dir, '.'.join([file_prefix, ext]))
        template.stream(state_chart=state_chart,
                        file_prefix=file_prefix).dump(output)


def main():
    parser = argparse.ArgumentParser(
        description='Generates the statechart corresponding C code.')
    parser.add_argument('-o',
                        '--output',
                        default='.',
                        help='code output directory')
    parser.add_argument('-sc',
                        '--state_chart',
                        required=True,
                        type=argparse.FileType('r'),
                        help='statechart declaration file')
    args = parser.parse_args()

    try:
        state_chart = load(args.state_chart)
    except LoadingError as exc:
        print('Failed to load {}: {}'.format(args.state_chart.name, str(exc)))
        sys.exit(1)

    code(state_chart, args.output)


if __name__ == '__main__':
    main()
