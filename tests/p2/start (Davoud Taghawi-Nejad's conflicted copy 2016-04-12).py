from __future__ import division
from myagent import MyAgent
from youragent import YourAgent
from abcEconomics import Simulation


def main():
    parameters = {
        'name': 'name',
        'num_rounds': 10
    }

    s = Simulation(parameters)
    action_list = [  # (('myagent', 'youragent'), 'compute'),
        ('youragent', 's'),
        ('myagent', 'g')]
    s.add_action_list(action_list)

    s.build_agents(MyAgent, 50000)
    s.build_agents(YourAgent, 50000)

    s.run(parallel=True)


if __name__ == '__main__':
    main()
