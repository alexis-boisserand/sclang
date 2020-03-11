import os
from subprocess import Popen, PIPE
from jinja2 import Environment, FileSystemLoader, StrictUndefined

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
                      lstrip_blocks=True,
                      undefined=StrictUndefined)
    template = env.get_template('graph.jinja')
    with Popen(['java', '-jar', plantuml_bin, '-p'], stdin=PIPE,
               stdout=PIPE) as proc:
        template.stream(state_chart=state_chart).dump(proc.stdin,
                                                      encoding='utf-8')
        proc.stdin.close()
        return proc.stdout.read()
