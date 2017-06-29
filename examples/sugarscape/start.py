"""
Sugarscape ({G1}, {M, T}) -- Epstein Chapter 4
Heavily use Mesa for space.
"""

from agents import Sugar, Spice, SsAgent
from abce import Simulation
from mesa.space import MultiGrid
from functools import reduce
import pylab


def main():
    s = Simulation(rounds=800, processes=1)
    grid = MultiGrid(50, 50, True)

    # build sugar and spice
    sugar_distribution = pylab.genfromtxt("sugar-map.txt")
    spice_distribution = sugar_distribution.T
    sugars = []
    spices = []
    for _, x, y in grid.coord_iter():
        max_sugar = sugar_distribution[x, y]
        max_spice = spice_distribution[x, y]
        sugar = Sugar((x, y), max_sugar)
        spice = Spice((x, y), max_spice)
        sugars.append(sugar)
        spices.append(spice)
        grid.place_agent(sugar, (x, y))
        grid.place_agent(spice, (x, y))

    # build agents
    agents = s.build_agents(SsAgent, 'SsAgent', 100,
                            parameters={'grid': grid})

    prices = []
    for r in s.next_round():
        for sugar in sugars:
            sugar.step()
        for spice in spices:
            spice.step()
        agents.do("move")
        agents.do("eat")
        pss = agents.do("trade_with_neighbors")
        prices_1p = [ps for ps in pss if ps]
        # flatten
        prices_1p = [p for ps in prices_1p for p in ps]
        mean_price = reduce(lambda x, y: x * y, prices_1p, 1) ** (1 / len(prices_1p))
        prices.append(mean_price)
    pylab.plot(prices)
    pylab.xlabel("Time")
    pylab.ylabel("Mean Price")
    pylab.savefig("prices.png")


if __name__ == '__main__':
    main()
