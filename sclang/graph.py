import sys
import os
from subprocess import Popen, PIPE
from jinja2 import Environment, FileSystemLoader, StrictUndefined

current_dir = os.path.dirname(__file__)
template_dir = os.path.join(current_dir, 'templates')
plantuml_bin = os.path.join(current_dir, 'plantuml', 'plantuml.jar')


def add_unique_name_attr(root_state):
    names = dict()
    for state in root_state.all_states:
        count = names.get(state.name, 0)
        state.unique_name = state.name + count * '_'
        names[state.name] = count + 1


def graph(root_state):
    add_unique_name_attr(root_state)
    env = Environment(loader=FileSystemLoader(template_dir),
                      trim_blocks=True,
                      lstrip_blocks=True,
                      undefined=StrictUndefined)
    template = env.get_template('graph.jinja')
    with Popen(['java', '-jar', plantuml_bin, '-p'], stdin=PIPE,
               stdout=PIPE) as proc:
        template.stream(root_state=root_state).dump(proc.stdin,
                                                    encoding='utf-8')
        proc.stdin.close()
        return proc.stdout.read()
