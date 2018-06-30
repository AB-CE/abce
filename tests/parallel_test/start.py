from __future__ import division
from myagent import MyAgent
from abcEconomics import Simulation


def main():
    s = Simulation()

    a = s.build_agents(MyAgent, 'myagent', 10000)
    for r in range(50):
        s.advance_round(r)
        a.do("compute")
    s.finalize()


if __name__ == '__main__':
    main()
