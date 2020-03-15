import os
import sys
import argparse
from ..parser import parse, ParsingError
from ..code import code

current_dir = os.path.dirname(__file__)
template_dir = os.path.join(current_dir, 'templates')


def main():
    parser = argparse.ArgumentParser(
        description='Generates the statechart corresponding C code.')
    parser.add_argument('state_chart',
                        type=argparse.FileType('r'),
                        help='statechart declaration file')
    parser.add_argument('-o',
                        '--output',
                        default='.',
                        help='code output directory')

    args = parser.parse_args()

    try:
        with args.state_chart:
            root_state = parse(args.state_chart.read())
    except ParsingError as exc:
        print('Failed to read {}: {}'.format(args.state_chart.name, str(exc)))
        sys.exit(1)

    code(root_state, args.output)


if __name__ == '__main__':
    main()
