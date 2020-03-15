import os
import sys
import argparse
from ..parser import parse, ParsingError
from ..graph import graph


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

    print(state_chart)
    #if args.output:
    #    output = args.output
    #else:
    #    base = os.path.splitext(os.path.basename(args.state_chart.name))[0]
    #    output_name = base + '.png'
    #    output = open(output_name, 'wb')
    #with output:
    #    output.write(graph(state_chart))


if __name__ == '__main__':
    main()
