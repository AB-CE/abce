""" This is a simple demonstration model how to integrate abcEconomics and mesa.
The model and scheduler specification are taken care of in
abcEconomics instead of Mesa.

Based on
https://github.com/projectmesa/mesa/tree/master/examples/boltzmann_wealth_model.

For further reading, see
[Dragulescu, A and Yakovenko, V. Statistical Mechanics of Money, Income, and Wealth: A Short Survey. November, 2002](http://arxiv.org/pdf/cond-mat/0211175v1.pdf)
"""
import abcEconomics as abce
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from moneyagent import MoneyAgent


def compute_gini(model):
    """ calculates the index of wealth distribution form a list of numbers """
    agent_wealths = model.wealths
    x = sorted(agent_wealths)
    N = len(x)
    B = sum(xi * (N - i) for i, xi in enumerate(x)) / (N * sum(x))
    return 1 + (1 / N) - 2 * B


class MoneyModel(abce.Simulation):  # The actual simulation must inherit from Simulation
    """ The actual simulation. In order to interoperate with MESA the simulation
    needs to be encapsulated in a class. __init__ sets the simulation up. The step
    function runs one round of the simulation. """

    def __init__(self, num_agents, x_size, y_size):
        super().__init__(name='abcEconomics and MESA integrated',
                         processes=1)
        # initialization of the base class. MESA integration requires
        # single processing
        self.grid = MultiGrid(x_size, y_size, True)
        self.agents = self.build_agents(MoneyAgent, 'MoneyAgent', num_agents,
                                        grid=self.grid)
        # abcEconomics agents must inherit the MESA grid
        self.running = True
        # MESA requires this
        self.datacollector = DataCollector(
            model_reporters={"Gini": compute_gini})
        # The data collector collects a certain aggregate value so the graphical
        # components can access them

        self.wealths = [0 for _ in range(num_agents)]
        self.r = 0

    def step(self):
        """ In every step the agent's methods are executed, every set the round
        counter needs to be increased by self.next_round() """
        self.advance_round(self.r)
        self.agents.move()
        self.agents.give_money()
        self.wealths = self.agents.report_wealth()
        # agents report there wealth in a list self.wealth
        self.datacollector.collect(self)
        # collects the data
        self.r += 1


if __name__ == '__main__':
    """ If you run model.py the simulation is executed without graphical
    representation """
    money_model = MoneyModel(1000, 20, 50)
    for r in range(100):
        print(r)
        money_model.step()
