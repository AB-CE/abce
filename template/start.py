from __future__ import division
from firm import Firm
from household import Household
from abce import Simulation, gui

simulation_parameters = {'name': 'name',
                         'firms': 5,
                         'households': 5}


# commend out simulation.graphs() and uncomment
# this line to run the simulation with a Graphical
#@gui(simulation_parameters) # User Interface
def main(simulation_parameters):
    simulation = Simulation(name='ABCEsimulation_name')

    simulation.declare_round_endowment(resource='labor_endowment',
                                       units=1,
                                       product='labor'
                                       )
    simulation.declare_perishable(good='labor')

    simulation.panel('household', possessions=['good1', 'good2'],  # put a list of household possessions to track here
                     variables=['utility'])  # put a list of household possessions to track here

    firms = simulation.build_agents(Firm, 'firm',
                                    number=simulation_parameters['firms'],
                                    parameters=simulation_parameters)
    households = simulation.build_agents(Household, 'household',
                                         number=simulation_parameters['households'],
                                         parameters=simulation_parameters)

    allagents = firms + households
    try:  # makes sure that graphs are displayed even when the simulation fails
        for r in range(50):
            simulation.advance_round(r)
            firms.do('one')
            households.do('two')
            allagents.do('three')
            households.do('panel')
    except Exception as e:
        print(e)
    finally:
        simulation.graphs()


if __name__ == '__main__':
    main(simulation_parameters)
