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

import abce
from mesa.space import MultiGrid
import pylab  # requires python3
from mesa.datacollection import DataCollector


def compute_gini(model):
    agent_wealths = model.wealths
    x = sorted(agent_wealths)
    N = model.num_agents
    B = sum( xi * (N-i) for i,xi in enumerate(x) ) / (N*sum(x))
    return (1 + (1/N) - 2*B)

class MoneyAgent(abce.Agent):
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

class Empty:
    pass

class MoneyModel:
    def __init__(self, num_agents, x, f):
        self.num_agents = num_agents
        self.s = abce.Simulation(rounds=300, processes=1)
        self.grid = MultiGrid(x, f, True)
        self.agents = self.s.build_agents(MoneyAgent, 'MoneyAgent', num_agents,
                            parameters={'grid': self.grid})
        self.schedule = Empty()
        self.schedule.agents = self.agents
        self.running = True

        self.datacollector = DataCollector(
            model_reporters={"Gini": compute_gini},)
            #agent_reporters={"Wealth": lambda a: a.report_wealth()})

    def step(self):
        _ = self.s.next_round()
        self.agents.do('move')
        self.agents.do("give_money")
        self.wealths = self.agents.do("report_wealth")
        self.datacollector.collect(self)




if __name__ == '__main__':
    main()
