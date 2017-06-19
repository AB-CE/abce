from __future__ import division
from myagent import MyAgent
from abce import Simulation


def main():
    parameters = {'name': 'name',
                  'num_rounds': 50}

    s = Simulation(parameters)

    a = s.build_agents(MyAgent, 10000)
    for r in s.next_round():
        a.do("compute")


if __name__ == '__main__':
    main()
