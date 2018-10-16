from __future__ import division
from firm import Firm
from household import Household
from abcEconomics import Simulation, gui
from pprint import pprint

simulation_parameters = {'name': 'name',
                         'rounds': 2,
                         'firms': 3,
                         'households': 3}

# commend out simulation.graphs() and uncomment
# this line to run the simulation with a Graphical
#@gui(simulation_parameters) # User Interface


def main(simulation_parameters):
    simulation = Simulation(
        rounds=simulation_parameters['rounds'], processes=2)

    firms = simulation.build_agents(Firm, 'firm',
                                    number=simulation_parameters['firms'],
                                    parameters=simulation_parameters)
    households = simulation.build_agents(Household, 'household',
                                         number=simulation_parameters['households'],
                                         parameters=simulation_parameters)

    for round in simulation.next_round():
        print('one')
        (firms + households).do('one')
        #pprint({k: str(v) for k, v in simulation.mlist.items()})
        print('two')
        (firms + households).do('two')


if __name__ == '__main__':
    main(simulation_parameters)
