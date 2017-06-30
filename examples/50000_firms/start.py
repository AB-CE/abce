from __future__ import division
from myagent import MyAgent
from youragent import YourAgent
from abce import Simulation


def main():
    parameters = {
        'name': 'name',
        'rounds': 10
    }

    s = Simulation(rounds=parameters['rounds'], processes=8)

    myagents = s.build_agents(MyAgent, 'myagent', 50000)
    youragents = s.build_agents(YourAgent, 'youragent', 50000)

    for r in s.next_round():
        # (myagents+youragents).do('compute')
        youragents.do('s')
        myagents.do('g')


if __name__ == '__main__':
    main()
