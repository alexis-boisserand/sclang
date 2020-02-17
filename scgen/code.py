import os
import sys
import argparse
from jinja2 import Environment, FileSystemLoader
from .models import load, LoadingError
from .normalize import upper_case, lower_case, camel_case

current_dir = os.path.dirname(__file__)


def code(machine):
    template_dir = os.path.join(current_dir, 'templates')
    filters = {
        func.__name__: func
        for func in [upper_case, lower_case, camel_case]
    }
    env = Environment(loader=FileSystemLoader(template_dir),
                      trim_blocks=True,
                      lstrip_blocks=True)
    env.filters.update(filters)
    inputs = [('state_machine_header.jinja', 'h'),
              ('state_machine_impl.jinja', 'c')]
    file_prefix = lower_case(machine.name)
    for input_, ext in inputs:
        template = env.get_template(input_)
        output = '.'.join([file_prefix, ext])
        template.stream(machine=machine, file_prefix=file_prefix).dump(output)


def main():
    parser = argparse.ArgumentParser(
        description='Generates the statechart corresponding C code.')
    parser.add_argument('-m',
                        '--machine',
                        required=True,
                        type=argparse.FileType('r'),
                        help='statechart declaration file')
    args = parser.parse_args()

    try:
        machine = load(args.machine)
    except LoadingError as exc:
        print('Failed to load {}: {}'.format(args.machine.name, str(exc)))
        sys.exit(1)

    code(machine)


if __name__ == '__main__':
    main()
