class StateChart(object):
    def __init__(self, states):
        self.states = states


class State(object):
    def __init__(self, name, transitions):
        self.name = name
        self.transitions = transitions


class Transition(object):
    def __init__(self, target, event=None):
        self.target = target
        self.event = event
