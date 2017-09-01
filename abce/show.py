""" :code:`python -m abce.show` shows the simulation results in ./result/*  """
from .gui import graphs


def show():
    graphs({'name': 'show'})


if __name__ == '__main__':
    show()
