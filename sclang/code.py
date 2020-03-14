import os
from jinja2 import Environment, FileSystemLoader, StrictUndefined
from .normalize import upper_case, lower_case, camel_case, lower_camel_case

current_dir = os.path.dirname(__file__)
template_dir = os.path.join(current_dir, 'templates')


def type_naming_style(*args):
    return lower_case(*args) + '_t'


def pointer_naming_style(*args):
    return 'p' + camel_case(*args)


style = {
    'function': lower_case,
    'variable': lower_case,
    'pointer': lower_case,
    'field': lower_case,
    'type': type_naming_style,
    'constant': upper_case
}


def add_path_elements_attr(state_chart):
    for state in state_chart.all_states:
        path_elements = state.path.split('/')
        state.path_elements = list(path_elements)


def code(state_chart, output_dir):
    add_path_elements_attr(state_chart)
    env = Environment(loader=FileSystemLoader(template_dir),
                      trim_blocks=True,
                      lstrip_blocks=True,
                      undefined=StrictUndefined)
    env.filters.update(style)
    inputs = [('state_chart_header.jinja', 'h'),
              ('state_chart_impl.jinja', 'c')]
    file_prefix = lower_case(state_chart.name)
    for input_, ext in inputs:
        template = env.get_template(input_)
        output = os.path.join(output_dir, '.'.join([file_prefix, ext]))
        template.stream(state_chart=state_chart,
                        file_prefix=file_prefix,
                        **style).dump(output)
