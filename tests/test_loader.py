import os
import fsmgen

current_dir = os.path.dirname(__file__)

def local(file_name):
    return os.path.join(current_dir, file_name)

def test_simplest():
    with open(local('simplest.yaml'), 'r') as f:
        simplest = fsmgen.load(f)
        assert len(simplest.states) == 2
        assert simplest.states[0].id == "Occupied"