import os
from jinja2 import Environment, FileSystemLoader, StrictUndefined
from .normalize import upper_case, lower_case, camel_case

current_dir = os.path.dirname(__file__)
template_dir = os.path.join(current_dir, 'templates')


def type_naming_style(*args):
    return lower_case(*args) + '_t'


def pointer_naming_style(*args):
    return 'p' + camel_case(*args)


style = {
    'filename': lower_case,
    'function': lower_case,
    'variable': lower_case,
    'pointer': lower_case,
    'field': lower_case,
    'type': type_naming_style,
    'constant': upper_case
}


def add_handlers_attr(transition):
    start = transition.event_handler.state
    end = transition.target
    start_elements = start.path_elements
    end_elements = end.path_elements


def add_path_elements_attr(root_state):
    for state in root_state.all_states:
        path_elements = state.path.split('/')
        state.path_elements = list(path_elements)


def code(root_state, output_dir):
    add_path_elements_attr(root_state)
    env = Environment(loader=FileSystemLoader(template_dir),
                      trim_blocks=True,
                      lstrip_blocks=True,
                      undefined=StrictUndefined)
    env.filters.update(style)
    inputs = [('state_chart_header.jinja', 'h'),
              ('state_chart_impl.jinja', 'c')]
    file_prefix = style['filename'](root_state.name)
    for input_, ext in inputs:
        template = env.get_template(input_)
        output = os.path.join(output_dir, '.'.join([file_prefix, ext]))
        template.stream(root_state=root_state, **style).dump(output)
