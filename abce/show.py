""" :code:`python -m abce.show` shows the simulation results in ./result/*  """
from abce import abcegui


def show(open=True, new=1):
    abcegui.run(open=open, new=new)


if __name__ == '__main__':
    show()
