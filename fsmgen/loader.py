import yaml
from cerberus import schema_registry, Validator

__transition = {
    'event' : {
        'type' : 'string'
    },
    'target' : {
        'type' : 'string'
    }
}

__state = {
    'id' : {
        'type' : 'string'
    },
    'transitions' : {
        'type' : 'list',
        'schema' : 'transition'
    }

}

__schema = {
    'states' :
    {
        'type' : 'list',
        'schema' : 'state'
    }
}

schema_registry.add('transition', __transition)
schema_registry.add('state', __state)
__validator = Validator(schema=__schema)

def load(stream):
    obj = yaml.safe_load(stream)
    __validator.validate(obj)
    return obj