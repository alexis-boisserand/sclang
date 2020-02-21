from sclang.parser import parse


def test_simplest():
    input = '''
off
  BUTTON_PRESS -> on
  TIMEOUT -> off

on
  TIMEOUT -> off
'''

    sc = parse(input)
    assert len(sc.states) == 2
