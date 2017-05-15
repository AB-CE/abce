from __future__ import division
from myagent import MyAgent
from abce import Simulation


def main():
    parameters = {
    'name': 'name',
    'num_rounds': 50
    }

    s = Simulation(parameters)
    action_list = [('myagent', 'compute')]
    s.add_action_list(action_list)

    s.build_agents(MyAgent, 10000)

    s.run()

if __name__ == '__main__':
    main()
