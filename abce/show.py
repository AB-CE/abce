""" :code:`python -m abcEconomics.show` shows the simulation results in ./result/*  """
from .gui import graph


def show():
    graph({'name': 'show'})


if __name__ == '__main__':
    show()
