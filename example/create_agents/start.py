from __future__ import division
from firm import Firm
from household import Household
from messenger import Messenger
from abce import Simulation, gui

simulation_parameters = {'name': 'name',
                         'rounds':  10,
                         'firms': 1,
                         'households': 0}

                             # commend out simulation.graphs() and uncomment
                             # this line to run the simulation with a Graphical
#@gui(simulation_parameters) # User Interface
def main(simulation_parameters):
        simulation = Simulation(rounds=simulation_parameters['rounds'])
        action_list = [('messenger', 'messaging'),
                       (('firm', 'household'), 'receive_message'),
                       ('firm', 'add_household'),
                       ('firm', 'add_firm'),
                       ('firm', 'print_id'),
                       ('household', 'print_id'),
                       (('firm', 'household'), 'aggregate')]  # this instructs ABCE to save panel data as declared below
        simulation.add_action_list(action_list)

        simulation.declare_round_endowment(resource='labor_endowment',
                                           units=1,
                                           product='labor')

        simulation.declare_perishable(good='labor')

        simulation.aggregate('household', possessions=[],  # put a list of household possessions to track here
                                      variables=['count']) # put a list of household possessions to track here

        simulation.aggregate('firm', possessions=[],  # put a list of household possessions to track here
                                      variables=['count']) # put a list of household possessions to track here

        simulation.build_agents(Firm, 'firm',
                       number=simulation_parameters['firms'],
                       parameters=simulation_parameters, expandable=True)

        simulation.build_agents(Household, 'household',
                       number=simulation_parameters['households'],
                       parameters=simulation_parameters, expandable=True)

        simulation.build_agents(Messenger, 'messenger', 1)


        simulation.run()
        simulation.graphs()

if __name__ == '__main__':
    main(simulation_parameters)

