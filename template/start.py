from __future__ import division
from firm import Firm
from household import Household
from abce import Simulation, gui

simulation_parameters = {'name': 'name',
                         'rounds': 50,
                         'firms': 5,
                         'households': 5}

                             # commend out simulation.graphs() and uncomment
                             # this line to run the simulation with a Graphical
#@gui(simulation_parameters) # User Interface
def main(simulation_parameters):
        simulation = Simulation(rounds=simulation_parameters['rounds'])
        action_list = [('firm', 'one'),
                       ('household', 'two'),
                       ('all', 'three')
                       ('household', 'panel')]  # this instructs ABCE to save panel data as declared below
        simulation.add_action_list(action_list)

        simulation.declare_round_endowment(resource='labor_endowment',
                                           units=1,
                                           product='labor'
        )
        simulation.declare_perishable(good='labor')

        simulation.panel('household', possessions=['good1', 'good2'],  # put a list of household possessions to track here
                                      variables=['utility']) # put a list of household possessions to track here

        simulation.build_agents(Firm, 'firm',
                       number=simulation_parameters['firms'],
                       parameters=simulation_parameters)
        simulation.build_agents(Household, 'household',
                       number=simulation_parameters['households'],
                       parameters=simulation_parameters)


        simulation.run()
        simulation.graphs()

if __name__ == '__main__':
    main(simulation_parameters)

