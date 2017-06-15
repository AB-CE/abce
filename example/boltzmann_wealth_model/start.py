"""
A barebone example to illustrate how an ABCE simulation can be equipped with
Mesa's space library. The model and scheduler specification are taken care of in
ABCE instead of Mesa.

Based on
https://github.com/projectmesa/mesa/tree/master/examples/boltzmann_wealth_model.

For further reading, see
[Dragulescu, A and Yakovenko, V. Statistical Mechanics of Money, Income, and Wealth: A Short Survey. November, 2002](http://arxiv.org/pdf/cond-mat/0211175v1.pdf)
"""

import random

from abce import Agent, Simulation
from mesa.space import MultiGrid
import pylab


def compute_gini(wealths):
    wealths = sorted(wealths)
    N = len(wealths)
    B = sum(xi * (N - i) for i, xi in enumerate(wealths)) / (N * sum(wealths))
    return (1 + (1 / N) - 2 * B)


class MoneyAgent(Agent):
    def init(self, parameters, agent_parameters):
        self.grid = parameters["grid"]
        x = random.randrange(self.grid.width)
        y = random.randrange(self.grid.height)
        self.pos = (x, y)
        self.grid.place_agent(self, (x, y))
        self.wealth = random.randrange(2, 10)

    def move(self):
        possible_steps = self.grid.get_neighborhood(self.pos, moore=True, include_center=False)
        new_position = random.choice(possible_steps)
        self.grid.move_agent(self, new_position)

    def give_money(self):
        if self.wealth > 0:
            cellmates = self.grid.get_cell_list_contents([self.pos])
            if len(cellmates) > 1:
                other = random.choice(cellmates)
                other.wealth += 1
                self.wealth -= 1

    def report_wealth(self):
        return self.wealth


def main():
    s = Simulation(rounds=300, processes=1)
    grid = MultiGrid(10, 10, True)
    agents = s.build_agents(MoneyAgent, 'MoneyAgent', 200,
                            parameters={'grid': grid})
    gini = []
    for r in s.next_round():
        agents.do("move")
        agents.do("give_money")
        wealths = agents.do("report_wealth")
        gini.append(compute_gini(wealths))
    pylab.plot(gini)
    pylab.xlabel('time')
    pylab.ylabel('gini index')
    pylab.savefig("gini.png")


if __name__ == '__main__':
    main()
